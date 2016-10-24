from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, send, emit
import logging
from functools import partial
from uuid import uuid4

from node_pool import NodePool
from node import Node
from payload import Payload
from job import Job
from dispatch_manager import DispatchManager

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    """
    The homepage.

    Clients can go here to register as a consumer of jobs.

    When transitioned into a library ideally we would just have a script tag.

    """
    return render_template('index.html')

@socketio.on('connect')
def connect():
    """
    Handle a client initially connecting.
    Generate a temporary node with node id and give it to the client to confirm.
    """

    print ("Received new client connection")

    node = Node(socket_id = request.sid)
    # Create a new node
    NodePool.get_pool().add_new_node(node)

    node.emit('registration', node.to_dict())
    DispatchManager.get_manager().dispatch_job(job)

@socketio.on('job_results')
def get_results(result_data):
    """
    Client calls this after processing data.

    result_data will have a codes for the following states:
        0 : SUCCESS
        1 : FAILURE
    """
    print 'GOT RESULT'
    # possible error code
    code = result_data.get('code');
    if code == 0:
        print 'SUCCESS'
    elif code == 1:
        # Code path where we want to either stop a job or retry the nodes operations
        # FIXME add retry logic
        print 'FAILURE'
        return

    job_id = result_data.get('job_id')
    node_id = result_data.get('node_id')
    result = result_data.get('results')
    # free up resources
    NodePool.get_pool().free_node(node_id)

    #get the job and push the data to it
    DispatchManager.get_manager().get_job(job_id).append_result(result)

# our test data
payload = Payload(
    operation = \
    """
    var a = [];
    for (var x = 0; x < 10; x++) {
        a.push(x);
    }
    return a;
    """,
    data=[1]
)

job = Job(
    payload = payload,
    required_number_of_nodes = 1
)

# code to start server
if __name__ == '__main__':
    app.run(debug=True)
