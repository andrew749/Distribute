from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, send, emit
import logging
from functools import partial
from uuid import uuid4
from enum import Enum

from node_pool import NodePool
from node import Node
from payload import Payload
from job import Job
from dispatch_manager import DispatchManager

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger('main_requests')

@app.route('/')
def index():
    """
    The homepage.

    Clients can go here to register as a consumer of jobs.

    When transitioned into a library ideally we would just have a script tag.

    """
    print 'rendering template'
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

    logger.info({
        'node_id' : node.id,
        'socket_id' : request.sid
    })
    node.emit('registration', node.to_dict())

@socketio.on('unregister')
def unregister(data):
    print 'Got unregister command'
    NodePool.get_pool().remove_node(data.get('node_id'))

class StatusCodes:
    SUCCESS = 0
    FAILURE = 1

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
    if code == StatusCodes.SUCCESS:
        print 'SUCCESS'
    elif code == StatusCodes.FAILURE:
        # Code path where we want to either stop a job or retry the nodes operations
        # FIXME add retry logic
        print 'FAILURE'
        return

    job_id = result_data.get('job_id')
    node_id = result_data.get('node_id')
    result = result_data.get('results')

    # free up resources that are no longer being
    # used so they can be re-dispatched
    NodePool.get_pool().free_node(node_id)

    #get the job and push the data to it so that it can stitch the data
    DispatchManager.get_manager().get_job(job_id).append_result(result)

@app.route('/test')
def test():
    """
    Simple test method used for debugging currently to mock the full flow.
    """
    with open('test_operation.js') as f:
        # our test data
        payload = Payload(
            operation = f.read(),
            data=range(1000000)
        )

        job = Job(
            payload = payload,
            # use all aailable cluster nodes
            required_number_of_nodes = len(NodePool.get_pool().free_nodes)
        )
        DispatchManager.get_manager().dispatch_job(job, namespace = '/')
    return 'OK'

@app.route('/console')
def render_console():
    return render_template('console.html', number_of_nodes = NodePool.get_pool().get_free_node_count())

@app.route('/node_counts')
def get_node_counts():
    free_nodes = NodePool.get_pool().get_free_node_count()
    occupied_nodes = NodePool.get_pool().get_occupied_node_count()
    return jsonify({
        'free_nodes': free_nodes,
        'occupied_nodes': occupied_nodes
    })

@app.route('/running_jobs')
def running_jobs():
    job_dict = {x.id: x.to_dict() for x in DispatchManager.get_manager().\
                id_to_job_mappings.values()}
    return jsonify(
        job_dict
    )

@app.route('/dispatch_job', methods=['POST'])
def dispatch_job():
    data = request.get_json()
    code = data.get('code')
    number_of_nodes = int(data.get("number_of_nodes"))
    payload = Payload(
            operation = code,
            data=[1]
    )

    job = Job(
        payload = payload,
        # use all aailable cluster nodes
        required_number_of_nodes = number_of_nodes
    )

    DispatchManager.get_manager().dispatch_job(job, namespace = '/')

    return 'OK'

# code to start server
if __name__ == '__main__':
    socketio.run(app)
