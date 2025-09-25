#!/usr/bin/env bash
# Usage: ./trigger.sh <user> <repo> <token> <payload_json_path>
USER="$1"
REPO="$2"
TOKEN="$3"
PAYLOAD_PATH="$4"

if [ -z "$USER" ] || [ -z "$REPO" ] || [ -z "$TOKEN" ] || [ -z "$PAYLOAD_PATH" ]; then
  echo "Usage: ./trigger.sh <user> <repo> <token> <payload_json_path>"
  exit 1
fi

curl -X POST -H "Accept: application/vnd.github+json"   -H "Authorization: token $TOKEN"   https://api.github.com/repos/$USER/$REPO/dispatches   -d "{"event_type":"fulfill-order","client_payload":$(cat "$PAYLOAD_PATH")}"
