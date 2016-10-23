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

    Clients can go here to register as a consumer of jobs.

    When transitioned into a library ideally we would just have a script tag.

    """
    return render_template('index.html')

#sample body for a payload
javascript_payload = \
"""
console.log('ola');
"""

@socketio.on('connect')
def connect():
    """
    Handle a client initially connecting.
    Generate a temporary node with node id and give it to the client to confirm.
    """
    print ("Received new client connection")

    node = Node()

    print ("Created new temporary Processing node with id %s" % node.id)

    emit('registration', node.to_dict())

@socketio.on('registration_complete')
def registration_complete(data):
    """
    A client calls this to confirm registration handshake.
    """
    node_id = data.get('node_id')
    manager.add_new_node(Node(node_id))

    print 'Registered node with id %s' % node.id

    # At this point the node is in our system and we can dispatch request to it.

@socketio.on('job_results')
def get_results(result_data):
    """
    Client calls this after processing data.

    result_data will have a codes for the following states:
        0 : SUCCESS
        1 : FAILURE
    """
    # possible error code
    code = result_data.get('code');
    if code == 0:
        print 'SUCCESS'
    elif code == 1:
        print 'FAILURE'


# code to start server
if __name__ == '__main__':
    app.run(debug=True)
