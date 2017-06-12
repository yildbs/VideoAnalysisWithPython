import threading
import queue
import time
import cv2


class FrameViewer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._frame_buffer = queue.Queue(100)
        self._interval = 33 # ms
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

            cv2.imshow('frame', frame)
            cv2.waitKey(1)

            elapsed_time = time.time() - start_time
            delay_time = 1 / 30 - elapsed_time
            if delay_time > 0:
                time.sleep(1 / 30)
            print('delay_time', delay_time * 1000, elapsed_time * 1000)