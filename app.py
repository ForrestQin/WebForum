from flask import Flask, request, jsonify, abort, make_response
import secrets
from datetime import datetime
import threading

app = Flask(__name__)

# In-memory storage for posts
posts = {}
posts_lock = threading.Lock()

def create_post_key():
    return secrets.token_hex(32)

@app.route('/post', methods=['POST'])
def create_post():
    if not request.json or 'msg' not in request.json or not isinstance(request.json['msg'], str):
        abort(400)

    with posts_lock:
        post_id = max(posts.keys(), default=0) + 1
        post_key = create_post_key()
        timestamp = datetime.utcnow().isoformat()

        posts[post_id] = {
            'id': post_id,
            'key': post_key,
            'timestamp': timestamp,
            'msg': request.json['msg'],
        }

    return jsonify({
        'id': post_id,
        'key': post_key,
        'timestamp': timestamp,
    })

@app.route('/post/<int:post_id>', methods=['GET'])
def read_post(post_id):
    with posts_lock:
        post = posts.get(post_id)

    if post is None:
        abort(404)

    return jsonify({
        'id': post['id'],
        'timestamp': post['timestamp'],
        'msg': post['msg'],
    })

@app.route('/post/<int:post_id>/delete/<string:post_key>', methods=['DELETE'])
def delete_post(post_id, post_key):
    with posts_lock:
        post = posts.get(post_id)

        if post is None:
            abort(404)

        if post['key'] != post_key:
            abort(403)

        del posts[post_id]
        timestamp = datetime.utcnow().isoformat()

    return jsonify({
        'id': post_id,
        'key': post_key,
        'timestamp': timestamp,
    })

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'err': 'Not Found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'err': 'Bad Request'}), 400)

@app.errorhandler(403)
def forbidden(error):
    return make_response(jsonify({'err': 'Forbidden'}), 403)

if __name__ == '__main__':
    app.run(debug=True)
