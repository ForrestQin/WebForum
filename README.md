# REST API for Posts and Users

This REST API allows you to manage posts and users. You can create, retrieve, and delete posts, as well as register,
authenticate, and edit user metadata.

## Endpoints

### Posts

1. **Create a new post**
    - Endpoint: `/post` (POST)
    - Payload: JSON with 'msg' key and optionally 'user_id' and 'user_key'
    - Response: Newly created post's 'id', 'key', and 'timestamp'

2. **Retrieve a post by ID**
    - Endpoint: `/post/<int:post_id>` (GET)
    - Response: Post's 'id', 'timestamp', 'msg', and 'user_id' (if available)

3. **Delete a post by ID and key**
    - Endpoint: `/post/<int:post_id>/delete/<string:post_key>` (DELETE)
    - Response: Deleted post's 'id', 'key', 'timestamp', and 'user_id' (if available)

### Users

4. **Register a new user**
    - Endpoint: `/user/register` (POST)
    - Payload: JSON with 'username', 'password', and optionally 'email', 'name', and 'avatar'
    - Response: Registered user's 'user_id' and 'user_key'

5. **Authenticate a user**
    - Endpoint: `/user/login` (POST)
    - Payload: JSON with 'username' and 'password'
    - Response: Authenticated user's 'user_id' and 'user_key'

6. **Retrieve a user's metadata**
    - Endpoint: `/user/<int:user_id>/metadata` (GET)
    - Response: User's 'username', 'email', 'name', and 'avatar'

7. **Edit a user's metadata**
    - Endpoint: `/user/<int:user_id>/metadata` (PUT)
    - Payload: JSON with 'user_key' and optionally 'name' and 'avatar'
    - Response: Updated user's 'username', 'email', 'name', and 'avatar'

### Post Search

8. **Search for posts by date**
    - Endpoint: `/posts/search` (GET)
    - Query Parameters: 'start_date' and 'end_date'
    - Response: List of posts that match the given date range

9. **Retrieve all posts by a user**
    - Endpoint: `/posts/user/<int:user_id>` (GET)
    - Response: List of posts created by the given user

10. **Search for posts based on content**
    - Endpoint: `/search` (GET)
    - Query Parameter: 'query'
    - Response: List of posts whose content matches the given query


