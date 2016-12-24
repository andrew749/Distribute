from flask import Flask, render_template, jsonify, request, Response, send_file
from flask_socketio import SocketIO, send, emit
import logging
from functools import partial
from uuid import uuid4
from enum import Enum

from model.node_pool import NodePool
from model.node import Node
from model.payload import Payload
from model.job import Job
from model.dispatch_manager import DispatchManager

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger('main_requests')

"""
API METHODS
"""

@app.route('/')
def index():
    """
    The homepage.

    Clients can go here to register as a consumer of jobs.

    When transitioned into a library ideally we would just have a script tag.

    """
    print 'rendering template'
    return render_template('index.html')

@app.route('/get-job-status/<job_id>')
def get_job_status(job_id):
    job = DispatchManager.get_manager().get_job(job_id)

    if job is not None:
        return jsonify({'status' : job.get_job_status()})

    # the client tried to query a job that doesnt exist
    raise Exception

@app.route('/job_console')
def render_console():
    return render_template(
        'console.html',
        number_of_nodes = NodePool.get_pool().get_free_node_count()
    )

@app.route('/node_counts')
def get_node_counts():
    # server stats
    free_nodes = NodePool.get_pool().get_free_node_count()
    occupied_nodes = NodePool.get_pool().get_occupied_node_count()

    return jsonify({
        'free_nodes': free_nodes,
        'occupied_nodes': occupied_nodes
    })

@app.route('/running_jobs')
def running_jobs():

    # show all the current jobs for this server session
    job_dict = {
        x.id: x.to_dict() for x in DispatchManager.get_manager().id_to_job_mappings.values()
    }

    return jsonify(
        job_dict
    )

@app.route('/dispatch_job', methods=['POST'])
def dispatch_job():
    data = request.get_json()
    code = data.get('code')
    number_of_nodes = int(data.get("number_of_nodes"))
    payload_data = data.get('payload_data', None)

    payload = Payload(
        operation = code,
        data=payload_data
    )

    job = Job(
        payload = payload,
        # use all available cluster nodes
        required_number_of_nodes = number_of_nodes
    )

    DispatchManager.get_manager().dispatch_job(job, namespace = '/')

    return 'OK'

@app.route('/get-job-data/<job_id>')
def get_job_data(job_id):
    job = DispatchManager.get_manager().get_job(job_id)
    if not job:
        raise Exception("Couldnt find a job with that id")
    path = job.get_full_result()
    print path
    return send_file(path, as_attachment=True, attachment_filename = job.get_filename() )

"""
METHODS FOR SOCKET CLIENT
"""
@socketio.on('connect')
def connect():
    """
    Handle a client initially connecting.
    Generate a temporary node with node id and give it to the client to confirm.
    """

    node = Node(socket_id = request.sid)

    logger.debug("Received new client connection with node id: {}".format(request.sid))

    # Create a new node using the singleton pool manager
    NodePool.get_pool().add_new_node(node)

    # tell the node that it is registered
    node.emit('registration', node.to_dict())

@socketio.on('unregister')
def unregister(data):

    # clients should call this method so that we know when they die
    logger.debug('Got unregister command from node:'.format(data.get('node_id')))

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

        job_id = result_data.get('job_id')
        node_id = result_data.get('node_id')
        result = result_data.get('results', None)

        #get the job and push the data to it so that it can stitch the data
        DispatchManager.get_manager().get_job(job_id).append_result(result)

    elif code == StatusCodes.FAILURE:
        # Code path where we want to either stop a job or retry the nodes operations
        # FIXME add retry logic
        print 'FAILURE:\n Node Id {node_id}\nJob Id {job_id}'.format(
            {'node_id':result_data.get('node_id'),
             'job_id': result_data.get('job_id')})
        return

    # free up resources that are no longer being
    # used so they can be re-dispatched
    NodePool.get_pool().free_node(node_id)

# code to start server
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
