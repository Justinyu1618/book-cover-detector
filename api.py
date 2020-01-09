import os
from flask import Flask, session, request, jsonify
from read_cover import read_cover
from retrieve_info import *
import time

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
	try:
		start = time.time()
		if request.method == "GET":
			image_file = request.args.get("image")  #base64 encoded image
			ISBN, am_link = read_cover(image_file, isfile=True)
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

	except Exception as e:
		print(f"ERROR: {e}")

	print(f"TOTAL: {time.time() - start}")
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
		if data:
			response['success'] = True 
			response['data'] = data
	except Exception as e:
		print(f"ERROR: {e}")

	return jsonify(response)
	

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
