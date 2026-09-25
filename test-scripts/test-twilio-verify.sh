#!/usr/bin/env bash

# Sends and checks one SMS verification using the Poker Night Twilio Verify service.
set -euo pipefail

readonly VERIFY_SERVICE_ITEM='PokerNight Twilio Verify Service SID'
readonly TWILIO_API_KEY_ITEM='Twilio PokerNight API Key'
readonly VERIFY_SERVICE_FIELD='credential'
readonly API_KEY_SID_FIELD='username'
readonly API_KEY_SECRET_FIELD='credential'

cleanup() {
  unset twilio_api_key_sid twilio_api_key_secret twilio_verify_service_sid verification_code
}

usage() {
  cat <<'EOF'
Usage: test-twilio-verify.sh

Reads the Poker Night Twilio Verify configuration from 1Password, prompts for a
test phone number and received code, then prints Twilio's non-secret API result.
EOF
}

read_op_field() {
  local item_name=$1
  local field_label=$2

  op item get "$item_name" --fields "label=${field_label}" --reveal --format json |
    plutil -extract 'value' raw -
}

if [[ $# -gt 1 || "${1:-}" == '--help' || "${1:-}" == '-h' ]]; then
  usage
  exit $([[ $# -eq 1 ]] && echo 0 || echo 2)
fi

if ! command -v op >/dev/null 2>&1; then
  echo 'The 1Password CLI (op) is required.' >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo 'curl is required.' >&2
  exit 1
fi

if ! command -v plutil >/dev/null 2>&1; then
  echo 'plutil is required.' >&2
  exit 1
fi

trap cleanup EXIT

twilio_verify_service_sid=$(read_op_field "$VERIFY_SERVICE_ITEM" "$VERIFY_SERVICE_FIELD")
twilio_api_key_sid=$(read_op_field "$TWILIO_API_KEY_ITEM" "$API_KEY_SID_FIELD")
twilio_api_key_secret=$(read_op_field "$TWILIO_API_KEY_ITEM" "$API_KEY_SECRET_FIELD")

read -r -p 'Test phone number in E.164 format (for example, +19715551212): ' test_phone
if [[ ! "$test_phone" =~ ^\+[1-9][0-9]{7,14}$ ]]; then
  echo 'The test phone number must be in E.164 format.' >&2
  exit 2
fi

send_response=$(curl --silent --show-error --write-out $'\n%{http_code}' \
  --user "${twilio_api_key_sid}:${twilio_api_key_secret}" \
  --data-urlencode "To=${test_phone}" \
  --data-urlencode 'Channel=sms' \
  "https://verify.twilio.com/v2/Services/${twilio_verify_service_sid}/Verifications")
send_status=${send_response##*$'\n'}
send_body=${send_response%$'\n'*}

if [[ "$send_status" != '200' && "$send_status" != '201' ]]; then
  echo "Twilio rejected the verification request (HTTP ${send_status}):" >&2
  printf '%s\n' "$send_body" >&2
  exit 1
fi

echo 'Verification requested. Enter the code received by SMS.'
read -r -s -p 'Verification code: ' verification_code
echo

check_response=$(curl --silent --show-error --write-out $'\n%{http_code}' \
  --user "${twilio_api_key_sid}:${twilio_api_key_secret}" \
  --data-urlencode "To=${test_phone}" \
  --data-urlencode "Code=${verification_code}" \
  "https://verify.twilio.com/v2/Services/${twilio_verify_service_sid}/VerificationCheck")
check_status=${check_response##*$'\n'}
check_body=${check_response%$'\n'*}

if [[ "$check_status" != '200' && "$check_status" != '201' ]]; then
  echo "Twilio rejected the verification check (HTTP ${check_status}):" >&2
  printf '%s\n' "$check_body" >&2
  exit 1
fi

printf '%s\n' "$check_body"