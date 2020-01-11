import os
from flask import Flask, session, request, jsonify, render_template, url_for
from read_cover import read_cover
from retrieve_info import *
import time
from werkzeug.utils import secure_filename
import base64, requests, json

AMAZON_IMG_URL = "http://images.amazon.com/images/P/%s.01._SCLZZZZZZZ_.jpg"
app = Flask(__name__, instance_relative_config=True)

@app.route("/get_data", methods=["GET", "POST"])
def get_data():
	response = {
		'primary_data': None,
		'secondary_data': None,
		'success': False
	}

	data_type = request.args.get("data_type")
	do_prim = data_type == "primary" or data_type is None
	do_second = data_type == "secondary" or data_type is None
	print(do_prim, do_second)

	if True: #try:
		start = time.time()
		ISBN = None
		if do_prim:
			if request.method == "GET":
				if("image" not in request.args):
					return open("index.html","r").read()
				image_file = request.args.get("image")  #base64 encoded image
				result = read_cover(image_file, isfile=True)
			elif request.method == "POST":
				if 'file' in request.files:
					file = request.files['file']
					if file.filename == '':
						return "No File Found"
					image = base64.b64encode(file.read()).decode("utf-8")
					result = read_cover(image)
				else:
					image_b64 = request.get_json()["image"]
					result = read_cover(image_b64)
			if result:
				ISBN, am_link = result
				response["image_link"] = AMAZON_IMG_URL % ISBN
			else:
				print("NO ISBN FOUND! :(")
				return jsonify(response)

			print(f"COVER: {time.time() - start}")
			mid = time.time()
			primary = retrieve_primary_info(ISBN)
			primary["isbn"] = ISBN
			print(f"PRIMARY: {time.time() - mid}")
			if primary:
				response['success'] = True 
				response['primary_data'] = primary

		if ISBN is None:
			if "isbn" in request.args: 
				ISBN = request.args.get("isbn")
			else:
				return "ISBN not found in parameters"

		if do_second:
			late = time.time()
			secondary = retrieve_secondary_info(ISBN)
			print(f"SECONDARY: {time.time() - late}")
			if secondary:
				response['success'] = True 
				response['secondary_data'] = secondary

	# except Exception as e:
	# 	print(f"ERROR in api: {e}")

	print(f"TOTAL: {time.time() - start}")
	print(response)
	return jsonify(response)

@app.route("/receive_file", methods=["POST"])
def receive_file():
	print(request.files)
	if 'file' not in request.files:
		print("bruh")
		return "No File Found"
	file = request.files['file']
	if file.filename == '':
		print("bruh2")
		return "No File Found"
	# filename = secure_filename(file.filename)
	image = base64.b64encode(file.read()).decode("utf-8")
	data = {"image": image}
	resp = requests.post(f'http://0.0.0.0:5000/get_data?data_type=primary', json=data)
	print(resp.json())
	return jsonify(resp.json())

@app.route("/", methods=["GET"])
def home():
	return open("index.html","r").read()
	

if __name__ == '__main__':
	if os.environ.get("SETTING") == "prod":
		with open("~/.amazon-product-api", 'w') as file:
			access_key = os.environ.get("AMAZON_ACCESS_KEY")
			secret_key = os.environ.get("AMAZON_SECRET_KEY")
			associate_tag = os.environ.get("ASSOCIATE_KEY")
			creds = f"[Credentials]\naccess_key={access_key}\nsecret_key={secret_key}\nassociate_tag={associate_tag}"
			file.write(creds)
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
