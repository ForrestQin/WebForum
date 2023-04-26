from flask import Flask, request, jsonify, abort, make_response
import secrets
from datetime import datetime
import threading

app = Flask(__name__)

# In-memory storage for posts
posts = {}
posts_lock = threading.Lock()
users = {}
user_id_counter = 1


def create_post_key():
	return secrets.token_hex(32)


@app.route('/post', methods=['POST'])
def create_post():
	print("create_post")
	if not request.json or 'msg' not in request.json or not isinstance(request.json['msg'], str):
		abort(400)

	user_id = request.json.get('user_id')
	user_key = request.json.get('user_key')

	if user_id and user_key:
		if not user_id in users or users[user_id].user_key != user_key:
			abort(403)

	with posts_lock:
		post_id = max(posts.keys(), default=0) + 1
		post_key = create_post_key()
		timestamp = datetime.utcnow().isoformat()

		posts[post_id] = {
			'id': post_id,
			'key': post_key,
			'timestamp': timestamp,
			'msg': request.json['msg'],
			'user_id': user_id if user_id and user_key else None,
		}

	return jsonify({
		'id': post_id,
		'key': post_key,
		'timestamp': timestamp,
	})


@app.route('/post/<int:post_id>', methods=['GET'])
def read_post(post_id):
	print("read_post")
	with posts_lock:
		post = posts.get(post_id)

	if post is None:
		abort(404)

	response = {
		'id': post['id'],
		'timestamp': post['timestamp'],
		'msg': post['msg'],
	}

	if post.get('user_id'):
		response['user_id'] = post['user_id']

	return jsonify(response)


@app.route('/post/<int:post_id>/delete/<string:post_key>', methods=['DELETE'])
def delete_post(post_id, post_key):
	print("delete_post")
	with posts_lock:
		post = posts.get(post_id)

		if post is None:
			abort(404)

		user_id = post.get('user_id')

		if post['key'] != post_key:
			if user_id and users[user_id].user_key == post_key:
				pass  # Allow deletion by user_key
			else:
				abort(403)

		del posts[post_id]
		timestamp = datetime.utcnow().isoformat()

	response = {
		'id': post_id,
		'key': post_key,
		'timestamp': timestamp,
	}

	if user_id:
		response['user_id'] = user_id

	return jsonify(response)


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'err': 'Not Found'}), 404)


@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'err': 'Bad Request'}), 400)


@app.errorhandler(403)
def forbidden(error):
	return make_response(jsonify({'err': 'Forbidden'}), 403)


from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/user/register', methods=['POST'])
def register():
	print("register")
	global user_id_counter
	data = request.get_json()
	username = data.get('username')
	password = data.get('password')

	if not username or not password:
		return jsonify({'err': 'Missing username or password'}), 400

	if username in [user.username for user in users.values()]:
		return jsonify({'err': 'Username already exists'}), 400

	user = User(username)
	user.set_password(password)
	user.user_key = secrets.token_hex(64)
	users[user_id_counter] = user
	user_id = user_id_counter
	user_id_counter += 1

	return jsonify({'user_id': user_id, 'user_key': user.user_key}), 201


@app.route('/user/login', methods=['POST'])
def login():
	print("login")
	data = request.get_json()
	username = data.get('username')
	password = data.get('password')

	if not username or not password:
		return jsonify({'err': 'Missing username or password'}), 400

	user_id = None
	for uid, user in users.items():
		if user.username == username:
			user_id = uid
			break

	if not user_id or not users[user_id].check_password(password):
		return jsonify({'err': 'Invalid username or password'}), 401

	return jsonify({'user_id': user_id, 'user_key': users[user_id].user_key}), 200


class User:
	def __init__(self, username):
		self.username = username
		self.password_hash = None
		self.user_key = None

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


if __name__ == '__main__':
	app.run(debug=True)
