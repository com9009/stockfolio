import queue
import threading
import time

    

class WorkerQueue:

    def __init__(self, timeout):

        self.q = queue.Queue()
        self.timeout = timeout

    
    def add(self, order):
        work = threading.Thread(target=order)
        self.q.put(work)

    
    def work_loop(self):
        while True:
            t = self.q.get()
            t.start()
            time.sleep(self.timeout)


    def start(self, queue_state=False):
        loop = threading.Thread(target=self.work_loop)

