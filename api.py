import os
from flask import Flask, session, request, jsonify, render_template, url_for
from read_cover import read_cover
from retrieve_info import *
import time
from werkzeug.utils import secure_filename
import base64, requests, json

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
	print(do_second, do_prim)
	if True: # try:
		start = time.time()
		if request.method == "GET":
			if("image" not in request.args):
				return open("index.html","r").read()
			image_file = request.args.get("image")  #base64 encoded image
			ISBN, am_link = read_cover(image_file, isfile=True)
		else:
			if 'file' in request.files:
				file = request.files['file']
				if file.filename == '':
					return "No File Found"
				image = base64.b64encode(file.read()).decode("utf-8")
				ISBN, am_link = read_cover(image)
			else:
				image_b64 = request.get_json()["image"]
				ISBN, am_link = read_cover(image_b64)
		if not ISBN:
			return "NO ISBN FOUND! :("
		print(f"COVER: {time.time() - start}")

		if do_prim:
			mid = time.time()
			primary = retrieve_primary_info(ISBN)
			primary["isbn"] = ISBN
			primary["amazon"] = am_link
			print(f"PRIMARY: {time.time() - mid}")
			if primary:
				response['success'] = True 
				response['primary_data'] = primary

		if do_second:
			late = time.time()
			secondary = retrieve_secondary_info(ISBN)
			print(f"SECONDARY: {time.time() - late}")
			if secondary:
				response['success'] = True 
				response['secondary_data'] = secondary

	# except Exception as e:
	# 	print(f"ERROR: {e}")

	print(f"TOTAL: {time.time() - start}")
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
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
