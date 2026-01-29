from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["github_events"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "push":
        author = data["pusher"]["name"]
        branch = data["ref"].split("/")[-1]
        msg = f'{author} pushed to {branch} on {datetime.utcnow()} UTC'
    elif event_type == "pull_request":
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f'{author} submitted a pull request from {from_branch} to {to_branch} on {datetime.utcnow()} UTC'
    else:
        msg = f'Unhandled event type: {event_type}'

    collection.insert_one({"message": msg})
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    events = list(collection.find().sort("_id", -1))
    return render_template('index.html', events=events)

if __name__ == '__main__':
    app.run(port=5000, debug=True)