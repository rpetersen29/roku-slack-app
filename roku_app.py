import os
from flask import Flask, request, jsonify, json
from roku import Roku
from slackclient import SlackClient

app = Flask(__name__)

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

def discover_roku():
	# this gives an 'IndexError: list index out of range' error if no roku is found
	# TODO: handle this better
	roku = Roku.discover(timeout=10)
	print(roku)
	return roku

roku = discover_roku()

def chunk_list(list, n):
	return [list[i:i + n] for i in range(0, len(list), n)]

@app.route('/remote', methods=['POST'])
def show_roku_remote():
	print(roku.commands)
	return jsonify(
		text="Press button to execute",
		response_type="ephemeral",
		attachments=[
			{
	            "actions": [
	                {
	                    "name": "command",
	                    "color": "#4a357d",
	                    "text": command,
	                    "type": "button",
	                    "value": command
	                } for command in commands
	            ],
	            "callback_id": "command"
        	} for commands in chunk_list(roku.commands, 5)
    	]
	)

@app.route('/apps', methods=['POST'])
def show_roku_apps():
	print(roku.apps)
	return jsonify(
		text="Press app button to launch",
		response_type="ephemeral",
		attachments=[
			{
	            "actions": [
	                {
	                    "name": "app",
	                    "color": "#4a357d",
	                    "text": app.name,
	                    "type": "button",
	                    "value": app.name
	                } for app in apps
	            ],
	            "callback_id": "app"
        	} for apps in chunk_list(roku.apps, 5)
    	]
	)

@app.route('/command', methods=['POST'])
def command_roku():
	payload = json.loads(request.form['payload'])
	if payload['callback_id'] == 'app':
		app = payload['actions'][0]['value']
		roku[app].launch()
		print(app + " launched")
	elif payload['callback_id'] == 'command':
		button = payload['actions'][0]['value']
		command = getattr(roku, button)
		command()
		print(button + " pressed")
	return ''

if __name__ == '__main__':
	app.run(debug=False)
