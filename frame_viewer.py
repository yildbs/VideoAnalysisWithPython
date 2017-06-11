import threading
import queue
import time
import cv2


class FrameViewer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._frame_buffer = queue.Queue(100)
        self._interval = 30 # ms
        self._enabled = True

    def set_interval(self, interval):
        self._interval = interval

    def set_enabled(self, enabled):
        self._enabled = enabled

    def push_frame(self, frame):
        try:
            self._frame_buffer.put(frame, block=True)
            # self._frame_buffer.put(frame, block=False)
        except:
            pass

    def run(self):
        while self._enabled is True:
            start_time = time.time()
            frame = self._frame_buffer.get(block=True)
            elapsed_time = time.time() - start_time
            delay_time = int(self._interval - elapsed_time * 1000)
            if delay_time <= 1:
                delay_time = 1
            cv2.imshow('frame', frame)
            print('delay_time', delay_time, elapsed_time)
            cv2.waitKey(delay_time)

