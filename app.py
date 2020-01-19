from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt 
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token)


app = Flask(__name__)

#app.config['MONGO_DBNAME'] = 'mongotask'
app.config["MONGO_URI"] = "mongodb://devtotti:jankulovski@newclustera-shard-00-00-c85ej.mongodb.net:27017,newclustera-shard-00-01-c85ej.mongodb.net:27017,newclustera-shard-00-02-c85ej.mongodb.net:27017/anonymousApp?ssl=true&replicaSet=NewClusterA-shard-0&authSource=admin&retryWrites=true&w=majority"
app.config["JWT_SECRET_KEY"] = 'secret'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


CORS(app)



##########################################################################################################################################################################################################################################################################################################################
@app.route("/login")
def login():
	return render_template("login.html")



@app.route("/register")
def register():
	return render_template("register.html")



@app.route("/post")
def post():
	return render_template("post.html")


############################################################################################################################################################################################################################################################################################################################





@app.route("/users/register", methods=['POST'])
def subscribe():
	users = mongo.db.anonymuser

	if request.method == 'POST':
		nick_name = request.form['nickname']
		email = request.form['email']
		password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
		created = datetime.utcnow()

		response = users.find_one({'nick_name':nick_name})
		if response:
			result = ({"Oops!":"User with the nick name already exist, try another name"})

		else:

			user_id = users.insert({
				'nick_name': nick_name,
				'email': email,
				'password': password,
				'created': created,
				})

			#new_db = mongo.db.nick_name

			new_user = users.find_one({'_id': user_id})

			result = {'nick_name': new_user['nick_name']+' registered'}

	else:
		pass


	return jsonify({'result':result})



@app.route("/users/post", methods=['POST'])
def post_anonym():

	messagedb = mongo.db.anonymessage
	users = mongo.db.anonymuser


	if request:
		friend_nick = request.form['friend_nick']
		message = request.form['message']
		created = datetime.utcnow()

		response = users.find_one({'nick_name':friend_nick})

		if response:
			user_message = messagedb.insert({'friend_nick':friend_nick,'message': message,'created': created})

			new_post = messagedb.find_one({'_id':user_message})

			result = {'message':new_post['message']}
			print("Done!")

		else:
			result = ({"Oops!":"User with the nick name do not exist"})

	else:
		result = {'error':'Invalid request'}


	return jsonify(result)




#############################################################################################################################################
#For test



"""@app.route("/users/posts", methods=['GET'])
def get_posts():
	messagedb = mongo.db.anonymessage
	result = []
	for field in messagedb.find():
		result.append({'user':str(field['friend_nick']),'message':str(field['message']), 'date':str(field['created'])})

	return jsonify(result)


@app.route("/users/register", methods=['GET'])
def get_users():
	users = mongo.db.anonymuser
	result = []
	for field in users.find():
		result.append({'nick':str(field['nick_name']),'email':str(field['email']),'password':str(field['password'])})

	return jsonify(result)"""




#############################################################################################################################################





@app.route("/users/login", methods=['POST'])
def get_anonym():
	users = mongo.db.anonymuser
	messagedb = mongo.db.anonymessage

	if request.method == "POST":
		nick_name = request.form['nickname']
		password = request.form['password']

		response = users.find_one({'nick_name':nick_name})

		if response:
			if bcrypt.check_password_hash(response['password'], password):
				access_token = create_access_token(identity = {
					'nick_name': response['nick_name'],
					'email': response['email']
					})

				result = []
				for field in messagedb.find():

					if str(nick_name) == str(field['friend_nick']):
						result.append({'message':str(field['message']), 'date':str(field['created'])})
						print("Data retrieved")

					else:
						result = ({"Oops!":"No one has sent you message yet"})


			else:
				result = ({"Oops!": "Invalid Username or Password"})


		else:
			result = ({"Oops!": "No user with details found"})


	return jsonify({'result': result})


if __name__ == '__main__':
	app.run(port=5117, debug=True)
