from flask import Flask, request, jsonify, send_from_directory
from flask_httpauth import HTTPBasicAuth
# import debugpy

import json
import os

app = Flask(__name__)
app.config['DEBUG'] = True

auth = HTTPBasicAuth()

users = {
  "admin": "admin",  # Change this to your desired username and password
}

@auth.verify_password
def verify_password(username, password):
  if username in users and users[username] == password:
    return username


@app.route('/')
@auth.login_required
def index():
  return send_from_directory('static', 'app.html')


@app.route('/all-presence', methods=['GET'])
@auth.login_required
def get_all_presence():
  try:
    with open('presence.json', 'r') as f:
      if f.read().strip():
        f.seek(0)
        json_data = json.load(f)
      else:
        json_data = []
    return jsonify({'status': 'success', 'data': json_data}), 200
  except Exception as e:
    app.logger.error(f"Error: {str(e)}")
    return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/presence', methods=['POST'])
@auth.login_required
def update_presence():
  data = request.json

  if not os.path.exists('presence.json'):
    with open('presence.json', 'w') as f:
      f.write(json.dumps([]))
  try:
    with open('presence.json', 'r') as f:
      if f.read().strip():
        f.seek(0)
        json_data = json.load(f)
      else:
        json_data = []

    date_entry = next(
      (entry for entry in json_data if entry['date'] == data['date']), None)
    if date_entry is None:
      date_entry = {'date': data['date'], 'names': []}
      json_data.append(date_entry)

    name_entry = next(
      (entry
       for entry in date_entry['names'] if entry['name'] == data['name']),
      None)
    if name_entry is None:
      name_entry = {'name': data['name'], 'present': False, 'paid': False}
      date_entry['names'].append(name_entry)

    # Update 'present' and/or 'paid' based on incoming data
    if 'present' in data:
      name_entry['present'] = data['present']
    if 'paid' in data:
      name_entry['paid'] = data['paid']

    with open('presence.json', 'w') as f:
      f.write(json.dumps(json_data))

    return jsonify({'status': 'success'}), 200
  except Exception as e:
    app.logger.error(f"Error: {str(e)}")
    return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/presence', methods=['GET'])
@auth.login_required
def get_presence():
  date = request.args.get('date')

  if not os.path.exists('presence.json'):
    with open('presence.json', 'w') as f:
      f.write(json.dumps([]))

  try:
    with open('presence.json', 'r') as f:
      if f.read().strip():
        f.seek(0)
        json_data = json.load(f)
      else:
        json_data = []

    date_entry = next((entry for entry in json_data if entry['date'] == date),
                      None)

    if date_entry is None:
      return jsonify({
        'status': 'error',
        'message': 'No entries for this date.'
      })

    return jsonify({'status': 'success', 'data': date_entry}), 200
  except Exception as e:
    app.logger.error(f"Error: {str(e)}")
    return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0")
