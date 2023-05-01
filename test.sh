#!/bin/sh

set -e
trap 'kill $PID' EXIT

./run.sh &
PID=$!

sleep 5

newman run forum_test_collection.postman_collection.json --env-var baseUrl=http://127.0.0.1:5000 --bail
