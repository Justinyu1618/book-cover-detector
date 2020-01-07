import os
from flask import Flask, session, request
from 

app = FLask(__name__, instance_relative_config=True)

@app.route("/get_data", methods=["POST"])
def get_data():
	payload = request.get_json()
	image = payload['image']  #base64 encoded image
	ISBN = read_cover(image)
	info = retrieve_info(ISBN)

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
