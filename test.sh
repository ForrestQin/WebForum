#!/bin/sh

set -e
trap 'kill $PID' EXIT

./run.sh &
PID=$!

newman run forum_multiple_posts.postman_collection.json -e env.json
newman run forum_post_read_delete.postman_collection.json -n 50
