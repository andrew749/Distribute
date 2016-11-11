from flask_socketio import SocketIO, send, emit
from uuid import uuid4
from model.node_pool import NodePool

class Node:
    """
    Properties:
        current_job_id: the id that this node is currently associated with
        id: the primary key id of this node
    """
    current_job_id = None

    def __init__(self, id = None, socket_id = None):
        if id is None:
            self.id = str(uuid4())
        else:
            self.id = id

        self.socket_id = socket_id

        print ("Created new node with id %s" % self.id)

    def set_job(self, job_id):
        self.current_job_id = job_id

    def finish(self):
        self.current_job_id = None

        # Free this node up to allow for more processing
        NodePool.get_pool().free_node(self.id)

    def is_registered(self):
        return self.socket_id != None

    def is_processing(self):
        return self.current_job_id != None

    def dispatch_job(self, event, payload_function, namespace = None):
        """
        Helper to allow emission of event to particular node
        rather than all nodes in a namespace
        """
        data = {
            'job_id': str(self.current_job_id),
            'payload_operation': payload_function
        }
        emit(event, data, room=self.socket_id, namespace = namespace)

    def emit(self, event, data):
        emit(event, data, room=self.socket_id)

    def to_dict(self):
        return {
            'node_id': str(self.id),
            'job_id': self.current_job_id,
        }
