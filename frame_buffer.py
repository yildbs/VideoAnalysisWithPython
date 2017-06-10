import threading


class FrameBuffer():
    def __init__(self, max_size=30):
        self._max_size = max_size
        self._lock = threading.Lock()
        self._condition = threading.Condition()
        self._buffer = []

    def push(self, item):
        try:
            print('Framebuffer try')
            self._lock.acquire()
            print('Framebuffer acquire')
            if len(self._buffer) >= self._max_size:
                del self._buffer[0]
            self._buffer.append(item)
            try:
                print('Framebuffer condition try')
                self._condition.acquire()
                print('Framebuffer condition acquire')
                self._condition.notify()
            finally:
                self._condition.release()
                print('Framebuffer condition release')
        finally:
            self._lock.release()
            print('Framebuffer release')

    def pop_front(self):
        data = []
        if len(self._buffer) is 0:
            print('popfront wait')
            try:
                self._condition.acquire()
                self._condition.wait()
            finally:
                self._condition.release()
        try:
            self._lock.acquire()
            data = self._buffer.pop(0)
        finally:
            self._lock.release()
        return data

    def get_latest(self):
        data = []
        try:
            self._lock.acquire()
            if len(self._buffer) is 0:
                print('get_latest wait')
                self._lock.release()
                try:
                    self._condition.acquire()
                    self._condition.wait()
                finally:
                    self._condition.release()
                self._lock.acquire()
            data = self._buffer[-1]
        finally:
            self._lock.release()
        return data