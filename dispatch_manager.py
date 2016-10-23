from uuid import uuid4
import json

class DispatchManager:

    # all the live jobs currently happening
    id_to_job_mappings = {}

    def __init__(self):
        self.pool = NodePool()

    def dispatch_job(self, job):
        self.id_to_job_mappings[job.id] = job

    def remove_job(self, job_id):
        job = self.id_to_job_mappings.pop(job_id)
        if job is not None:
            for x in job.active_nodes:
                x.unset_job()

    def add_new_node(self, node):
        self.pool.add_new_node(node)

    def remove_node(self, node_id):
        self.pool.pop_processing_node(node_id)

class Job:
    required_number_of_nodes = 0
    active_nodes = {}
    payload = None

    def __init__(self, payload, required_number_of_nodes):
        self.id = uuid4()
        self.required_number_of_nodes = required_number_of_nodes
        self.payload = payload

    def add_processing_node(self, node):

        self.active_nodes[node.id] = node

    def pop_processing_node(self, node_id):
        #TODO add logic to distribute data if failed to another node
        self.active_nodes.pop(node_id)

class Payload:

    # string of the bound function to execute
    payload = None

    def __init__(self, code_to_run, data):
        self.payload = self._build_javascript_method(code_to_run, data)
        self.payload_data = data
        self.payload_function = code_to_run

    def _build_javascript_method(func, **kwargs):
        new_body = ""
        for x in kwargs.items():
            new_body += "var {variable_name} = {variable_data};\n".format(
                variable_name = x[0],
                variable_data = x[1]
            )
        new_body += func
        return new_body

    def to_dict(self):
        return  {
            'payload_operation': self.payload,
        }

class NodePool:
    """
    A pool manager for nodes to distribute available resources.
    """
    # mapping id to nodes which are free for processing
    free_nodes = {}

    # mapping id to nodes which are currently being used
    occupied_nodes = {}

    def __init__(self):
        pass

    def add_new_node(self, node):
        self.free_nodes[node.id] = node

    def remove_node(self, node_id):
        self.free_nodes.pop(node_id)
        self.occupied_nodes.pop(node_id)

    def consume_free_node(self):
        node = self.free_nodes.pop()
        self.occupied_nodes.append(node)
        return node

    def free_node(self, node_id):
        """
        Free a currently occupied node.
        """
        node = self.occupied_nodes.pop(node_id)
        self.free_nodes[node.id] = node
        return node

    def consume_free_nodes(self, number_of_nodes):
        """
        Args:
            number_of_nodes: number of nodes that a client requests to process the request.
        """
        nodes = []
        for x in xrange(number_of_nodes):
            nodes.append(self.consume_free_node())
        return nodes

class Node:
    """
    Properties:
        current_job_id: the id that this node is currently associated with
        id: the primary key id of this node
    """
    current_job_id = None

    def __init__(self, id = None):
        if id is None:
            self.id = uuid4()
        else:
            self.id = id

    def set_job(self, job_id):
        self.current_job_id = job_id

    def unset_job(self):
        self.current_job_id = None

    def is_running(self):
        return self.current_job_id != None

    def to_dict(self):
        return {
            'node_id': str(self.id),
            'job_id': self.current_job_id,
        }
