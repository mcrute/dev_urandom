"""
Swarm -- A multiprocessing architecture for python 2.3

@author: Mike Crute (mcrute@ag.com)
@organization: American Greetings Interactive
@date: December 10, 2008
@version: $Rev$

Swarm is a multiprocessing module for Python 2.3. It's like the
multiprocessing module in Python 2.6 in some ways but its designed
to coordinate large pools of processess that only run tasks and
report their results.

A client should create a PoolManager and provision it for the jobs
they will want to run. Jobs can then be pushed into a run queue
which will be distributed to the child processes for processing.
Upon completion of the job each child will return a results object
which the manager will process.

Jobs should implement the Job interface below.
Results objects should implement the Results interface below.

There really aren't any rules around what a Job or a Results object
can do.

The PoolManager should be created and run in a seperate thread from
the program code that pushes stuff into the queue. Your jobs need
not be threadsafe since they will be run in a seperate process.
Results objects WILL need to be threadsafe since they will be run
by the PoolManager class.

CAUTIONARY NOTE:
Results objects should NOT do too much, especially blocking IO
since they will block further processing of the run queue which
is less than ideal.

API Spec (of sorts):
>>> class RecoveryJob(Job): pass
>>> class DeliveryJob(Job): pass
>>> class CleanupJob(Job): pass
>>> class SenderJob(Job): pass
>>> class StatsLogger(ResultHandler): pass
>>> 
>>> run_queue = Queue()
>>> 
>>> pool = PoolManager(size=10)
>>> pool.result_handler = StatsLogger()
>>> pool.run_queue = run_queue
>>> 
>>> pool.provision(RecoveryJob, max_workers=2)
>>> pool.provision(DeliveryJob, min_workers=1, max_workers=5)
>>> pool.provision(CleanupJob,  max_workers=2)
>>> pool.provision(SenderJob,   min_workers=3, max_workers=pool.MAX)
>>> 
>>> pool.spawn()
>>> 
>>> for count in range(0, 10):
>>>     run_queue.push(SenderJob())
"""


import os
import sys
import fcntl
import select
import cPickle as pickle
from Queue import Full as QueueFull, Empty as QueueEmpty


# Pipe Commands (these must be max 7 characters + \n
SHUTDOWN = "SHUTDWN\n"
SHUTTING_DOWN = "SHTNGDN\n"
RUN_COMMAND = "RUNCOMD\n"
COMMAND_DONE = "CMDDONE\n"

# Process Types
PARENT = "PARENT"
CHILD = "CHILD"


class Process(object):
    """
    This class serves different purposes depending on where it is
    being accessed. After the fork this becomes the primary command
    runner in the child process.

    In the parent process this class is used for process accounting
    as well as a simplified interface for applying jobs to the child
    and gather data back from the child. Aside from writes into the
    pipes the parent and child are unaware of other mutations to
    this class.

    API clients should generally NOT interact with this class but
    instead should use the PoolManager which knows how to wrangle
    these really well.
    """

    write_pipe = None
    read_pipe = None

    pid = None
    role = None

    def spawn(self):
        pipes = { "parent": {}, "child": {} }

        pipes[PARENT]["read"], pipes[CHILD]["write"] = os.pipe()
        pipes[CHILD]["read"], pipes[PARENT]["write"] = os.pipe()

        self.pid = os.fork()
        self.role = (self.pid is 0) and CHILD or PARENT

        self._setup_pipes(pipes)

        if self.role is CHILD:
            self.wait_for_job()
        else:
            return self

    def _setup_pipes(self, pipes):
        whoami_not = (self.role is PARENT) and CHILD or PARENT

        os.close(pipes[whoami_not]["read"])
        os.close(pipes[whoami_not]["write"])

        self.write_pipe = os.fdopen(pipes[whoami]["write"])
        self.read_pipe = os.fdopen(pipes[whoami]["read"])

    def wait_for_job(self):
        while True:
            command = self.read_pipe.read(8)

            if command is RUN_COMMAND:
                payload = self.read_pipe.readline()
                payload = pickle.loads(payload)
                self._run_job(payload)

            elif command is SHUTDOWN:
                self.shutdown()

    def _run_job(self, job):
        try:
            results = ""# do job
        except Exception, exc:
            results = exc

        results = pickle.dumps(results, pickle.HIGHEST_PROTOCOL)
        self.write_pipe.write(COMMAND_DONE)
        self.write_pipe.write(results)

    def shutdown(self):
        self.write_pipe.write(SHUTTING_DOWN)
        sys.exit()

    def apply_job(self, job):
        """Called by the parent, should pickle the job and write
        it into the child's write pipe.
        """
        pass


class PoolManager(object):

    MIN = 0
    MAX = 0

    def __init__(self, size=2, request_handler=None, run_queue=None,
                 sleep_time=0, process_cls=Process):
        self._wait_pool = []
        self._work_pool = {}
        self._pool_map = {}
        self.pool_size = size
        self.request_handler = request_handler
        self.run_queue = run_queue
        self.process_cls = process_cls
        self.sleep_time = sleep_time

    def provision(self, job_class, max_workers=1, min_workers=0):
        job_class = job_class.__name__

        if (self.MAX + max_workers) > self.pool_size:
            raise ValueError("Pool is full, try removing some jobs.")

        self._work_pool[job_name] = []
        self._pool_map[job_class] = (min_workers, max_workers)
        self._update_slot_count()

    def deprovision(self, job_class):
        job_class = job_class.__name__

        if job_class in self._pool_map:
            del self._pool_map[job_class]
            del self._work_pool[name]
            self._update_slot_count()

    def _get_slot_count(self):
        max_slots = []
        min_slots = []

        for _, slot_count in self._pool_map.items():
            min_slots.append(slot_count[0])
            max_slots.append(slot_count[1])

        return (sum(max_slots), sum(min_slots))

    def _update_slot_count(self):
        self.MIN, self.MAX = self._get_slot_count()

    def spawn(self):
        self.startup()

        for _ in range(1, self.pool_size):
            process = self.process_cls()
            self._wait_pool.append(process.spawn())

        self._run_jobs()

    def _run_jobs(self):
        """
        Empty the run queue and apply all the jobs to workers.
        If not enough workers for all jobs start polling for
        workers to become free, then apply the jobs to them.

        If the queue is empty start polling the read end of
        worker pipe and adding them back to the free stack.

        If all workers have been gathered back to the free stack
        check the run queue once more and sleep if sleep_time not
        0 else shut down all workers and return.
        """
        while not self.run_queue.empty():
            try:
                job = self.run_queue.get()
            except QueueEmpty:
                return # XXX: Wrong behavior

            if self.job_can_run(job):
                self.apply_job_to_worker(job)

    def can_handle_job(self, job):
        job_name = job.__class__.__name__

        if job_name not in self._pool_map:
            return False

        return True

    def job_can_run(self, job):
        job_name = job.__class__.__name__

        if not self.can_handle_job(job):
            return False

        max_workers = self._pool_map[job_name][1]
        used_workers = len(self._work_pool[job_name])

        if used_workers >= max_workers:
            return False

        return True

    def apply_job_to_worker(self, job):
        worker = self._wait_pool.pop()
        job_name = job.__class__.__name__

        self._work_pool[job_name].append(worker)
        worker.apply_job(job)

    def shutdown(self):
        """Subclasses are free to implement shutdown behvior.
        """
        pass

    def startup(self):
        """Subclasses are free tim implement startup behavior.
        """
        pass


class Job(object):

    def run(self, *args):
        pass

class JobResult(object):

    def __init__(self):
        pass


class ResultHandler(object):

    def __init__(self):
        pass
