import threading


class FrameBuffer():
    def __init__(self, max_size=30):
        self._max_size = max_size
        self._lock = threading.Lock()
        self._condition_cannot_pop = threading.Condition()
        self._condition_cannot_push = threading.Condition()
        self._buffer = []

    def push(self, item):
        try:
            print('Framebuffer try')
            self._lock.acquire()
            print('Framebuffer acquire')
            if len(self._buffer) >= self._max_size:
                #del self._buffer[0]
                self._lock.release()
                try:
                    print('_condition_cannot_push try')
                    self._condition_cannot_push.acquire()
                    print('_condition_cannot_push acquire')
                    self._condition_cannot_push.wait()
                finally:
                    self._condition_cannot_push.release()
                    print('_condition_cannot_push release')
                self._lock.acquire()


            self._buffer.append(item)
            try:
                print('Framebuffer condition try')
                self._condition_cannot_pop.acquire()
                print('Framebuffer condition acquire')
                self._condition_cannot_pop.notify()
            finally:
                self._condition_cannot_pop.release()
                print('Framebuffer condition release')
        finally:
            self._lock.release()
            print('Framebuffer release')

    def pop_front(self):
        data = []
        if len(self._buffer) is 0:
            print('popfront wait')
            try:
                self._condition_cannot_pop.acquire()
                self._condition_cannot_pop.wait()
            finally:
                self._condition_cannot_pop.release()
        try:
            self._lock.acquire()
            data = self._buffer.pop(0)
        finally:
            self._lock.release()

        try:
            self._condition_cannot_push.acquire()
            self._condition_cannot_push.notify_all()
        finally:
            self._condition_cannot_push.release()

        return data

    def get_latest(self):
        data = []
        try:
            self._lock.acquire()
            if len(self._buffer) is 0:
                print('get_latest wait')
                self._lock.release()
                try:
                    self._condition_cannot_pop.acquire()
                    self._condition_cannot_pop.wait()
                finally:
                    self._condition_cannot_pop.release()
                self._lock.acquire()
            data = self._buffer[-1]
        finally:
            self._lock.release()

        return data