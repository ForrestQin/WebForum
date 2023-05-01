#!/bin/sh

set -e
trap 'kill $PID' EXIT

./run.sh &
PID=$!

sleep 1

newman run forum_multiple_posts.postman_collection.json -e env.json # use the env file
newman run forum_post_read_delete.postman_collection.json -n 50 # 50 iterations

newman run forum_test_collection.postman_collection.json -e env_test.json # test extensions
