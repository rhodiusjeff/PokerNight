#!/usr/bin/env python3
"""Confirmed post-admission source synchronization. LOCAL MOD - HARVEST TO CPB."""

import pathlib
import hashlib
import importlib.util


spec = importlib.util.spec_from_file_location('publication_sync_owner', pathlib.Path(__file__).with_name('planning-publication.py'))
publication = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publication)
git = publication.planning_git.git
require = publication.contract.require
digest = publication.contract.digest


def head(root):
    return git(root, 'rev-parse', 'HEAD').stdout.decode().strip()


def branch(root):
    return git(root, 'symbolic-ref', '-q', 'HEAD', check=False).stdout.decode().strip()


def operation(root):
    for name in ('rebase-merge', 'rebase-apply', 'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD'):
        relative = git(root, 'rev-parse', '--git-path', name).stdout.decode().strip()
        filename = pathlib.Path(relative)
        if not filename.is_absolute():
            filename = pathlib.Path(root) / filename
        if filename.exists():
            return name
    return None


def resolution_digest(root):
    parts = [git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all').stdout,
             git(root, 'diff', '--binary', '--no-ext-diff').stdout,
             git(root, 'diff', '--cached', '--binary', '--no-ext-diff').stdout, head(root).encode()]
    return hashlib.sha256(b'\0'.join(parts)).hexdigest()


def clean(root):
    require(not git(root, 'status', '--porcelain=v1', '--untracked-files=all').stdout, 'preserve or commit dirty/staged/untracked work before synchronization; no automatic stash')


def offer(root, identity, selected_branch, method, confirmed):
    require(confirmed, 'sync offer fetch/verification requires explicit command confirmation')
    require(method in ('rebase', 'merge'), 'unknown synchronization method')
    root, directory, header = publication.load_attempt(root, identity)
    manifest = publication.contract.load_json(publication.evidence.confined(root, header['offer']['bundle']) / 'manifest.json')
    require(manifest.get('schema') == 'cp-change-admission-bundle-v1', 'source synchronization requires repository-format admission')
    require(operation(root) is None, 'another Git operation is in progress')
    require(selected_branch.startswith('refs/heads/') and branch(root) == selected_branch, 'select the current working branch explicitly')
    require(selected_branch != header['offer']['target_ref'], 'do not rewrite the operational target branch')
    clean(root)
    observed = publication.run_cli(root, identity, 'verify', True)
    require(observed['state'] == 'applied' and observed['application_verified'], 'verified normal admission required')
    target = observed['target_commit']
    git(root, 'fetch', '--quiet', '--no-tags', '--no-write-fetch-head', str(directory / 'repository'), target)
    source_head = head(root)
    base = header['offer']['target_commit']
    require(git(root, 'merge-base', '--is-ancestor', base, source_head, check=False).returncode == 0, 'working branch does not descend from the admission baseline')
    if method == 'rebase':
        require(not git(root, 'rev-list', '--merges', base + '..' + source_head).stdout, 'working branch has merges; use merge synchronization or explicit manual recovery')
    value = {'schema': 'cp-admission-sync-offer-v1', 'attempt_id': identity, 'branch': selected_branch,
             'source_head': source_head, 'base': base, 'target_commit': target, 'method': method,
             'admission_commit': observed.get('integration_commit', target)}
    return {'offer': value, 'offer_digest': digest(value)}


def current(root, identity):
    root, directory, header = publication.load_attempt(root, identity)
    events = publication.journal(root, directory)
    starts = [event['data'] for event in events if event['state'] == 'sync-started']
    last = next((event for event in reversed(events) if event['state'].startswith('sync-')), None)
    return root, directory, header, starts[-1] if starts else None, last


def status(root, identity):
    root, directory, header, started, last = current(root, identity)
    return {'attempt_id': identity, 'state': last['state'] if last else 'sync-not-started',
            'offer': started['offer'] if started else None, 'head': head(root), 'branch': branch(root),
            'operation': operation(root), 'resolution_digest': resolution_digest(root),
            'admission_remains_applied': any(event['state'] == 'applied' for event in publication.journal(root, directory))}


def finish(root, directory, identity, offered):
    value = offered['offer']
    require(operation(root) is None and branch(root) == value['branch'], 'synchronization has not finished on the selected branch')
    clean(root)
    target = value['target_commit']
    require(git(root, 'merge-base', '--is-ancestor', target, head(root), check=False).returncode == 0, 'synchronized branch does not contain the verified target')
    repository = publication.evidence.load_module('planning-repository')
    require(repository.snapshot(root, head(root))['state'] == repository.snapshot(root, target)['state'], 'replayed work changed admitted state; explicit reconciliation required')
    result = {'attempt_id': identity, 'state': 'sync-completed', 'branch': value['branch'], 'head': head(root),
              'target_commit': target, 'offer_digest': offered['offer_digest'], 'pushed': False}
    publication.append_event(root, directory, 'sync-completed', result)
    return result


def run(root, identity, action, offered, confirmation, confirmed):
    require(confirmed and action in ('start', 'continue', 'abort'), 'explicit synchronization action confirmation required')
    publication.evidence.attribution(confirmation)
    require(digest(offered['offer']) == offered['offer_digest'] and confirmation.get('offer_digest') == offered['offer_digest'], 'synchronization offer differs from confirmation')
    value = offered['offer']
    require(value['attempt_id'] == identity and confirmation.get('action') == action, 'synchronization action or attempt differs')
    root, directory, header, started, last = current(root, identity)
    valid_method = value.get('schema') == 'cp-admission-sync-offer-v1' and value['method'] in ('rebase', 'merge')
    valid_baseline = value['base'] == header['offer']['target_commit'] and value['branch'] != header['offer']['target_ref']
    require(valid_method and valid_baseline, 'invalid synchronization baseline or method')
    with publication.attempt_lock(root, directory):
        if last and last['state'] == 'sync-completed':
            require(last['data']['offer_digest'] == offered['offer_digest'] and head(root) == last['data']['head'], 'completed synchronization subject changed')
            return last['data']
        if action == 'start':
            require(started is None, 'existing synchronization requires status and owned recovery')
            require(operation(root) is None and branch(root) == value['branch'] and head(root) == value['source_head'], 'working branch moved or another Git operation is active')
            clean(root)
            verified = [event for event in publication.journal(root, directory) if event['state'] == 'applied']
            require(verified and verified[-1]['data']['target_commit'] == value['target_commit'], 'synchronization verification changed')
            client = publication.trial_client(root, header)
            require(client.branch(header['offer']['target_ref'].removeprefix('refs/heads/'))['commit'] == value['target_commit'], 'target moved since synchronization offer; verify and offer again')
            if value['method'] == 'rebase':
                require(confirmation.get('history_rewrite_acknowledged') is True, 'rebase requires explicit private/shared-history acknowledgement')
            publication.append_event(root, directory, 'sync-started', {'offer': value, 'offer_digest': offered['offer_digest'], 'confirmation': confirmation})
            arguments = ['rebase', '--onto', value['target_commit'], value['base'], value['branch'].removeprefix('refs/heads/')] if value['method'] == 'rebase' else ['merge', '--no-edit', value['target_commit']]
        else:
            require(started and started['offer_digest'] == offered['offer_digest'], 'synchronization is not owned by this offer')
            require(confirmation.get('resolution_digest') == resolution_digest(root), 'resolution changed since confirmation')
            expected_ops = ('rebase-merge', 'rebase-apply') if value['method'] == 'rebase' else ('MERGE_HEAD',)
            require(operation(root) in expected_ops, 'owned Git operation is not in progress; inspect before recovery')
            require(git(root, 'rev-parse', 'ORIG_HEAD').stdout.decode().strip() == value['source_head'], 'Git operation belongs to a different source head')
            if action == 'abort':
                retained = {'resolution_digest': resolution_digest(root), 'unstaged': git(root, 'diff', '--binary').stdout,
                            'staged': git(root, 'diff', '--cached', '--binary').stdout}
                for name in ('unstaged', 'staged'):
                    destination = directory / ('sync-abort-' + retained['resolution_digest'] + '-' + name + '.patch')
                    if not destination.exists():
                        publication.capture.publish_new_bytes(destination, retained[name])
            arguments = [value['method'], '--' + action]
        result = git(root, '-c', 'core.editor=true', *arguments, check=False)
        if result.returncode:
            observed = {'attempt_id': identity, 'state': 'sync-needs-reconciliation', 'operation': operation(root),
                        'resolution_digest': resolution_digest(root), 'admission_remains_applied': True}
            publication.append_event(root, directory, observed['state'], observed)
            return observed
        if action == 'abort':
            require(head(root) == value['source_head'], 'abort did not restore original source head')
            observed = {'attempt_id': identity, 'state': 'sync-aborted', 'head': head(root), 'admission_remains_applied': True}
            publication.append_event(root, directory, 'sync-aborted', observed)
            return observed
        return finish(root, directory, identity, offered)