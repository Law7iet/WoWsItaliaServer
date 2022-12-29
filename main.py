import os

import yaml
import secrets
from flask import Flask, request, render_template

from api import ApiMongoDB

app = Flask(__name__)
mongo = ApiMongoDB()
cfg = None
list = {}
with open(
  os.path.realpath(os.path.dirname(__file__)) + "/web_config.yaml", 'r') as ymlfile:
	cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


@app.route("/")
def home():
	return render_template("index.html")


@app.route("/queue")
def get_list():
	return list


@app.route("/create")
def create_url():
	discord_id = request.args.get("discord")
	id = secrets.token_hex(16)
	list[id] = discord_id
	redirect_uri = f"https://{cfg['public_web_ip']}/auth?id={id}"
	base_url = f"https://api.worldoftanks.eu/wot/auth/login/?application_id={cfg['app_id']}"
	final_url = f"{base_url}&redirect_uri={redirect_uri}"
	return final_url


@app.route('/auth')
def authentication():
	data: dict = {"status": 0, "content": {}}
	try:
		# Wargaming's API is correct
		if request.args.get('status') == 'ok':
			id = request.args.get('id')
			if id in list:
				# Get data
				nickname = request.args.get('nickname')
				discord = list.pop(id)
				wows = request.args.get('account_id')
				token = request.args.get('access_token')
				expiration = request.args.get('expires_at')
				# Search player
				searched_player = mongo.search_player(discord, wows)
				if searched_player:
					# Player found
					data["status"] = -1
					data["content"] = {
						"discord": searched_player["discord"],
						"wows": searched_player["wows"]
					}
				else:
					# Insert player
					inserted_player = mongo.insert_player(discord, wows, token, expiration)
					if inserted_player:
						# Player is inserted
						data["content"] = {
							"nickname": nickname,
							"discord": inserted_player["discord"],
							"wows": inserted_player["wows"]
						}
					else:
						# Player is not inserted
						data["status"] = -2
			else:
				print("HLO")
				# URL is already used
				data["status"] = -3
		else:
			# Wargaming's API is not correct
			data["status"] = -4
	except Exception as error:
		# General error
		data["status"] = -5
		data["content"] = {"error": str(error)}
	return render_template("authentication.html", data=data)


# main driver function
if __name__ == '__main__':
	app.run(host=cfg['bind_web_ip'], port=cfg['bind_web_port'], debug=True)
