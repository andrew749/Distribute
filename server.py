from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, send, emit
from dispatch_manager import *
import logging
from functools import partial
from uuid import uuid4

app = Flask(__name__)
socketio = SocketIO(app)

manager = DispatchManager()

@app.route('/')
def index():
    """
    The homepage.
    clients can go here to register as a consumer of jobs.
    """
    return render_template('index.html')

#sample body for a payload
javascript_payload = \
"""
console.log('ola');
"""

@socketio.on('connect')
def connect():
    print ("Received new client connection")

    node = Node()

    print ("Created new temporary Processing node with id %s" % node.id)

    emit('registration', node.to_dict())

@socketio.on('registration_complete')
def registration_complete(data):
    node_id = data.get('node_id')

    node = Node(node_id)

    manager.add_new_node(node)

    print 'Registered node with id %s' % node.id

    # At this point the node is in our system and we can dispatch request to it.

@socketio.on('job_results')
def get_results(result_data):
    # possible error code
    code = result_data.get('code');
    if not code == 0:
        print 'ERROR'
        return

    print code

# code to start server
if __name__ == '__main__':
    app.run(debug=True)
