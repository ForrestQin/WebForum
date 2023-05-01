import string

from flask import Flask, request, jsonify, abort, make_response, json
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
		timestamp = datetime.now().isoformat()

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
# update postman test case
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
	email = data.get('email', '')
	name = data.get('name', '')
	avatar = data.get('avatar', '')

	if not username or not password:
		return jsonify({'err': 'Missing username or password'}), 400

	if username in [user.username for user in users.values()]:
		return jsonify({'err': 'Username already exists'}), 400

	user = User(username, email, name, avatar)
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


@app.route('/user/<int:user_id>/metadata', methods=['GET'])
def get_user_metadata(user_id):
	user = users.get(user_id)
	if user is None:
		abort(404)

	return jsonify({
		'username': user.username,
		'email': user.email,
		'name': user.name,
		'avatar': user.avatar
	})


@app.route('/user/<int:user_id>/metadata', methods=['PUT'])
def edit_user_metadata(user_id):
	user = users.get(user_id)
	if user is None:
		abort(404)

	data = request.get_json()
	user_key = data.get('user_key')

	if user_key != user.user_key:
		abort(403)

	name = data.get('name')
	avatar = data.get('avatar')

	if name:
		user.name = name
	if avatar:
		user.avatar = avatar

	return jsonify({
		'username': user.username,
		'email': user.email,
		'name': user.name,
		'avatar': user.avatar
	})


class User:
	def __init__(self, username, email, name=None, avatar=None):
		self.username = username
		self.email = email
		self.name = name
		self.avatar = avatar
		self.password_hash = None
		self.user_key = None

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


@app.route('/posts/search', methods=['GET'])
def search_posts():
	start_date_str = request.args.get('start_date', None)
	end_date_str = request.args.get('end_date', None)

	try:
		start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
		end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
	except ValueError:
		return jsonify({'err': 'Invalid date format'}), 400

	result = []
	with posts_lock:
		for post in posts.values():
			post_date = datetime.fromisoformat(post['timestamp'])
			if (start_date is None or post_date >= start_date) and (end_date is None or post_date <= end_date):
				result.append({
					'id': post['id'],
					'timestamp': post['timestamp'],
					'msg': post['msg'],
					'user_id': post.get('user_id'),
				})

	return jsonify(result)


@app.route('/posts/user/<int:user_id>', methods=['GET'])
def get_posts_by_user(user_id):
	if user_id not in users:
		abort(404)

	with posts_lock:
		user_posts = [post for post in posts.values() if post.get('user_id') == user_id]

	return jsonify(user_posts)

def search(query, data):
    query_words = query.lower().translate(str.maketrans('', '', string.punctuation)).split()
    results = []

    for item in data:
        msg_words = item['msg'].lower().translate(str.maketrans('', '', string.punctuation)).split()
        if any(word in msg_words for word in query_words):
            results.append(item)

    return results


@app.route('/search', methods=['GET'])
def search_posts_based_content():
	query = request.args.get('query', '')

	if not query:
		abort(400)

	with posts_lock:
		results = search(query, posts.values())

	response = [
		{
			'id': post['id'],
			'timestamp': post['timestamp'],
			'msg': post['msg'],
			'user_id': post.get('user_id')
		} for post in results
	]

	return jsonify(response)


if __name__ == '__main__':
	app.run(debug=True)
