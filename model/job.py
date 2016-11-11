from model.node_pool import NodePool
from uuid import uuid4

class Job:
    """
    A Job that can be dispatched to a variety of nodes for processing.
    """

    def __init__(self, payload, required_number_of_nodes = 1):
        self.id = str(uuid4())
        self.required_number_of_nodes = required_number_of_nodes
        self.payload = payload
        self.active_nodes = {}
        self.success = False
        self.processing = False
        self.result = []
        self.received_results = 0

    def dispatch(self, namespace = None):
        """
        Distribute this work among the set nodes.
        """

        free_nodes = []
        # reserve nodes to process a job
        free_nodes += NodePool.get_pool().consume_free_nodes(self.required_number_of_nodes)

        # transform free_nodes to a usable mapping
        for x in free_nodes:
            # set these nodes to be processing this job
            x.set_job(self.id)

            # add them to the dict of node processing this job request
            self.active_nodes.update({x.id: x})

        node_counter = 0
        # split the payload data and send off jobs to all the nodes
        for x in self.payload.split_payload_data(self.required_number_of_nodes):
            self.active_nodes.values()[node_counter].dispatch_job('job_request',  x, namespace = namespace)
            node_counter += 1

        processing = True

    def append_result(self, result):
        self.received_results += 1

        # If this state is satisfied, we have all the parts from the dispatched jobs
        if self.received_results == self.required_number_of_nodes:
            self.success = True

        if not result:
            return

        if self.result == None:
            self.result = []

        self.result.extend(result)

    def finish(self):
        """
        Free up node resources so they can be used by other jobs.
        """
        for x in self.active_nodes.items():
            x[1].finish()

    def get_full_result(self):
        """
        If the result hasnt been requested yet, stich it together.
        Otherwise just return it.
        """
        if processing == True:
            raise JobStatusException(msg="Not done processing yet")

        if not self.success:
            raise JobStatusException(msg="Job was unsuccessful")

        return result

    def to_dict(self):
        return {
            'id': self.id,
            'required_number_of_nodes': self.required_number_of_nodes,
            'processing': self.processing,
            'success': self.success,
            'received_parts': self.received_results,
            'status': self.get_job_status()
        }

    def get_job_status(self):
        """
        Return the percentage complete a job is
        """
        return ( self.received_results / self.required_number_of_nodes ) * 100 \
                if not self.success else 100

    class JobResourceException(Exception):
        """
        Internal exception class to be used when there arent
        enough resources available.
        """
        def __init__(self, msg=None):
            super(JobException, self).__init__(msg=msg)

    class JobStatusException(Exception):
        """
        An exception for when operations are performed on an incomplete job
        """
        def __init__(self, msg=None):
            supet(JobStatusException, self).__init__(msg=msg)

