import logging
import sys
import time
import threading
import uuid
from queue import Queue
from collections import deque

import pykka
from pykka import ActorDeadError, ActorRef, ActorRegistry, messages

logger = logging.getLogger('pykka')

class Job:
    level = 0
    def __init__(self, level):
        self.level = level
        pass
        #job 정의


class ActorMultiLevelQueue(Queue):
    def __init__(self, maxsize=0, queue_level=1):
        self.maxsize = maxsize
        self.queue_level = queue_level
        self._init(maxsize, queue_level)

        # mutex must be held whenever the queue is mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # is shared between the three conditions, so acquiring and
        # releasing the conditions also acquires and releases mutex.
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item is added to the queue; a
        # thread waiting to get is notified then.
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item is removed from the queue;
        # a thread waiting to put is notified then.
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() is notified to resume
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def _init(self, maxsize, queue_level):
        self.queue = [deque() for i in range(queue_level)]

    def _qsize(self):
        return sum([len(queue) for queue in self.queue])

    def _put(self, envelope):
        job = envelope.message.args[0]
        if isinstance(job, Job):
            level = job.level
            self.queue[level].append(envelope)
        else:
            self.queue[-1].append(envelope)

    def _get(self):
        for sub_queue in self.queue:
            if len(sub_queue) != 0:
                return sub_queue.popleft()
        
class MutliLvelQueueActor(pykka.ThreadingActor):
    def __init__(self, queue_level, execute_interval):
        self.queue = ActorMultiLevelQueue(queue_level=queue_level)
        super().__init__()

    def _start(self):
        assert self.actor_ref is not None, (
            'Actor.__init__() have not been called. '
            'Did you forget to call super() in your override?'
        )
        ActorRegistry.register(self.actor_ref)
        logger.debug('Starting {}'.format(self))
        self._start_actor_loop()
        return self.actor_ref

    def _create_actor_inbox(self):
        return self.queue


class APIExecutor(MutliLvelQueueActor):
    def __init__(self, queue_level, interval):
        super().__init__(queue_level, interval)

        self._start()
        self.actor_proxy = self.actor_ref.proxy()

    def api_call(self, job):
        print(job)
        print(f"level {job.level} job {job} is executing...")
        time.sleep(1)



if __name__ == '__main__':
    api_executor = APIExecutor(queue_level=3, interval=0.1)
    executor_proxy = api_executor.actor_proxy
    for i in range(3):
        for level in range(2, -1, -1):
            job = Job(level=level)
            future = executor_proxy.api_call(job)

    while True:
        time.sleep(5)
        job = Job(level=0)
        executor_proxy.api_call(job)