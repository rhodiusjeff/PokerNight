# Tic-Tac-Toe: Design, Browser Targets And Repository Decision

Date: 2026-09-29
Context: ADHOC-7fd789738d5348cbbbd4f4cb378fbecf
Provenance: current Operator conversation, transcribed by GitHub Copilot.

## Operator: Testing And Destination (Verbatim)

```text
2- iPhone - Chrome browser on both iPhone and desktop
3 - don't worry about pokernight product scope, land it in this repo.
```

## Design Offered For Agreement

The assistant asked whether the Operator agreed to browser-held game state, Express
serving the app, a Start button after setup, and mode/mark changes disabled during play.

Operator response (verbatim):

```text
I agree with that design
```

## Operation Confirmation

The assistant offered these three operations for this context:

1. `/plan-work ADHOC-7fd789738d5348cbbbd4f4cb378fbecf --append`
2. `/plan-work ADHOC-7fd789738d5348cbbbd4f4cb378fbecf --canon`
3. `/plan-work ADHOC-7fd789738d5348cbbbd4f4cb378fbecf --work`

Operator response (verbatim):

```text
run all three
```

## Confirmed Meaning And Limits

- Required browser acceptance targets are Chrome on desktop and Chrome on a physical
  iPhone. Physical-phone testing over local Wi-Fi from source-4 remains required.
- The intended repository is this PokerNight repository. A separate product-scope
  objection must not continue to block planning. No particular Git target branch or
  operational baseline was selected by this statement.
- Game state is held in the browser; Express serves the app. The agreed design does
  not require a server gameplay API or shared multiplayer state.
- Initial setup has a Start button. Mode/mark settings cannot change while a game is
  active. This does not change the previously confirmed Play again behavior: reuse
  the selected mode/mark and begin another game after a human presses that button.

Exact device models, OS/browser versions and implementation dependency versions were
not supplied. Record actual tested versions later instead of inventing them. This is
not approval of extra Safari, Firefox or Android coverage from earlier recommendations.
No public network exposure, baseline initialization, commit, push, PR, merge, complete
proposal, admission or product implementation is authorized by these three operations.