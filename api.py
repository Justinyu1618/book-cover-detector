import os
from flask import Flask, session, request, jsonify
from read_cover import read_cover
from retrieve_info import retrieve_info

app = Flask(__name__, instance_relative_config=True)

@app.route("/get_data", methods=["GET", "POST"])
def get_data():
	response = {
		'data': None,
		'success': False
	}
	try:
		if request.method == "GET":
			image_file = request.args.get("image")  #base64 encoded image
			ISBN = read_cover(image_file, isfile=True)
		else:
			image_b64 = request.get_json()["image"]
			print(image_b64)
			ISBN = read_cover(image_b64)	

		if not ISBN:
			return "NO ISBN FOUND! :("
		info = retrieve_info(ISBN)
		if info:
			response['success'] = True 
			response['data'] = info
	except Exception as e:
		print(f"ERROR: {e}")

	return jsonify(response)
	

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
