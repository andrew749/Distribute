from uuid import uuid4
from flask_socketio import emit
import json

class DispatchManager:
    _manager = None

    def __init__(self):
        # all the live jobs currently happening
        self.id_to_job_mappings = {}

    @classmethod
    def get_manager(cls):
        """
        Method to treat the manger as a singleton
        """
        if not cls._manager:
            cls._manager = DispatchManager()

        return cls._manager

    def dispatch_job(self, job):
        print 'Adding job %s to dispatch manager' % job.id
        self.id_to_job_mappings[job.id] = job
        job.dispatch()

    def get_job(self, job_id):
        """
        Helper to get a job if it exists.

        Raises:
            JobDoesNotExistException
        """
        job =  self.id_to_job_mappings.get(job_id, None)

        return job

    def remove_job(self, job_id):
        job = self.id_to_job_mappings.pop(job_id)
        if job is not None:
            job.finish()
