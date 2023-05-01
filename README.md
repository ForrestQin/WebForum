# CS515 Project 2: Calculator Language
Honglin Qin hqin4@stevens.edu,
Siyan Liu sliu112@stevens.edu,
Yetong Chen ychen12@stevens.edu

This REST API allows you to manage posts and users. You can create, retrieve, and delete posts, as well as register, authenticate, and edit user metadata.

## Github repo
https://github.com/ForrestQin/WebForum

## Time
We spent about 25 hours on the project in total.

## Test 
Run `sudo ./setup.sh` or `./setup.sh` to install packages.
Run `sudo ./run.sh` or `./run.sh` to start the server.
Run `sudo ./test.sh` or `./test.sh` to test the code.

We tested our code using the postman collections `forum_test_collection.postman_collection.json`. The environment variables are in the `env_test.json`.

## Bugs or issues
Most of the bugs we encounter are related to TypeError and passing parameters.

## Resolved issue
We encountered some issues with passing parameters to endpoints. Parameters can be provided to endpoints through path, body, and query. Path parameters are included in the endpoint's URI, which resembles a web address. Body parameters, also known as payloads, contain the data that the endpoint is designed to manipulate. Here we use JSON format. Most endpoints that require a body parameter aim to modify the resource's data. Query parameters let users adjust the scope of the request to retrieve a subset of the resource, filtering out resources that don't match specific criteria such as name, type, size, or status. To create a query in a URI, add a question mark (`?`) at the end of the endpoint to indicate that query information is coming. The parameter name and value are then provided in the format `name=value`, with additional parameters separated by an ampersand (`&`). When we execute `POST /user/register`, we pass the parameters as a query and receive them as the body, with the endpoint not receiving the parameters directly. After understanding the three modes of passing parameters, we modified the mode of passing parameters for each endpoint.

## Baseline
**Create a new post**
   - Endpoint: `/post` (POST)
   - Payload: JSON with 'msg' key and optionally 'user_id' and 'user_key'
     ```json
     {
       "msg": "Hello World!",
       "user_id": 1,
       "user_key": "your_user_key"
     }
     ```
   - Response: Newly created post's 'id', 'key', and 'timestamp'

**Retrieve a post by ID**
   - Endpoint: `/post/<int:post_id>` (GET)
   - URL Parameter: `post_id`
   - Response: Post's 'id', 'timestamp', 'msg', and 'user_id' (if available)

**Delete a post by ID and key**
   - Endpoint: `/post/<int:post_id>/delete/<string:post_key>` (DELETE)
   - URL Parameters: `post_id`, `post_key`
   - Response: Deleted post's 'id', 'key', 'timestamp', and 'user_id' (if available)

## 5 extensions
### 1. Users and user keys
**Register a new user**
   - Endpoint: `/user/register` (POST)
   - Payload: JSON with `username`, `password`, and optionally `email`, `name`, and `avatar`
     ```json
     {
       "username": "Sam",
       "password": "password123",
       "email": "Sam@example.com",
       "name": "Sam",
       "avatar": "https://example.com/avatar.jpg"
     }
     ```
   - Response: Registered user's `user_id` and `user_key`. 
      `user_id` should be an integer, `user_key` should be a long, unique random string.

**Authenticate a user**
   - Endpoint: `/user/login` (POST)
   - Payload: JSON with `username` and `password`
     ```json
     {
       "username": "Sam",
       "password": "password123"
     }
     ```
   - Response: Authenticated user's `user_id` and `user_key`.
      `user_id` should be an integer, `user_key` should be a long, unique random string.

### 2. User profiles
**Retrieve a user's metadata**
   - Endpoint: `/user/<int:user_id>/metadata` (GET)
   - URL Parameter: `user_id`
   - Response: User's `username`, `email`, `name`, and `avatar`.
      All of them are strings.

**Edit a user's metadata**
   - Endpoint: `/user/<int:user_id>/metadata` (PUT)
   - URL Parameter: `user_id`
   - Payload: JSON with `user_key` and optionally `name` and `avatar`
     ```json
     {
       "user_key": "your_user_key",
       "name": "Sam",
       "avatar": "https://example.com/avatar.jpg"
     }
     ```
   - Response: Updated user's `username`, `email`, `name`, and `avatar`.
      All of them are strings.

### 3. Date- and time-based range queries
**Search for posts by date**
   - Endpoint: `/posts/search` (GET)
   - Query Parameters: `start_date` and `end_date`
     ```
     /posts/search?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
     ```
   - Response: List of posts that match the given date range

### 4. User-based range queries
**Retrieve all posts by a user**
   - Endpoint: `/posts/user/<int:user>`
   - URL Parameter: `user`
   - Response: List of posts created by that user
   
### 5. Fulltext search
**Search for posts by the post's content**
   - Endpoint: `/search` (GET)
   - Query Parameters: `query`
     ```
     /search?query=hello
     ```
   - Response: List of posts match the query

To test our endpoints, we write the following tests:
`POST /user/register` User 1 Registration
`POST /user/login` User 1 Login
`GET /user/{{user_id1}}/metadata` Get 1 User Metadata
`PUT /user/{{user_id1}}/metadata` Edit User 1 Metadata
`GET /user/{{user_id1}}/metadata` Get User 1 Metadata again
`POST /post` Create a Post by User 1
`GET /post/{{post_id1}}` Read the Post by User 1
`POST /user/register` User 2 Registration
`POST /user/login` User 2 Login
`POST /post` Create Post 2 by User 2
`GET /post/{{post_id2}}` Read the Post 2
`GET /posts/search?start_date={{post_timestamp1}}&end_date={{post_timestamp1}}` Search Posts by date and time
`GET /posts/user/{{user_id1}}` Search Posts by User
`GET /search?query=2` Fulltext search
`DEL /post/{{post_id2}}/delete/{{post_key2}}` Delete Post 2

To run these tests above, run `./test.sh` or `sudo ./test.sh`.