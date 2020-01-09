import os
from flask import Flask, session, request, jsonify
from read_cover import read_cover
from retrieve_info import *

app = Flask(__name__, instance_relative_config=True)

@app.route("/primary_data", methods=["GET", "POST"])
def primary_data():
	response = {
		'data': None,
		'success': False
	}
	try:
		if request.method == "GET":
			image_file = request.args.get("image")  #base64 encoded image
			ISBN, am_link = read_cover(image_file, isfile=True)
		else:
			image_b64 = request.get_json()["image"]
			ISBN, am_link = read_cover(image_b64)	

		if not ISBN:
			return "NO ISBN FOUND! :("

		data = retrieve_primary_info(ISBN)
		data["isbn"] = ISBN
		data["amazon"] = am_link

		if data:
			response['success'] = True 
			response['data'] = data
	except Exception as e:
		print(f"ERROR: {e}")

	return jsonify(response)

@app.route("/secondary_data", methods=["GET"])
def secondary_data():
	response = {
		'data': None,
		'success': False
	}
	try:
		ISBN = request.args.get("isbn")
		if not ISBN:
			return "NO ISBN FOUND! :("

		data = retrieve_secondary_info(ISBN)
		data["isbn"] = ISBN

		if data:
			response['success'] = True 
			response['data'] = data
	except Exception as e:
		print(f"ERROR: {e}")

	return jsonify(response)
	

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
