from threading import Thread
from queue import Queue

from time import sleep


class Observer:
    _queue = Queue()

    def __init__(self, handleEvent):
        self.handleEvent = handleEvent
        t = Thread(target=self.event_loop)
        t.daemon = True
        t.start()

    def queue(self, data):
        self._queue.put(data)

    def event_loop(self):
        while True:
            if self._queue.empty():
                sleep(0.001)
            else:
                self.handleEvent(self._queue.get())
