import os
from flask import Flask, session, request, jsonify
from read_cover import read_cover
from retrieve_info import retrieve_info

app = Flask(__name__, instance_relative_config=True)

@app.route("/get_data", methods=["GET"])
def get_data():
	payload = request.args.get("isbn")
	# image = payload['image']  #base64 encoded image
	ISBN = payload
	response = {
		'data': None,
		'success': False
	}

	try:
		# ISBN = read_cover(image)
		info = retrieve_info(ISBN)
		print(info)
		if info:
			response['success'] = True 
			response['data'] = info
	except Exception as e:
		print(f"ERROR: {e}")

	return jsonify(response)
	

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
