import cv2
import threading


class FrameProducer(threading.Thread):

    def __init__(self, file_name, queue):
        threading.Thread.__init__(self)
        self._file_name = file_name
        self._queue = queue

    def run(self):
        capture = cv2.VideoCapture(self._file_name)

        while True:
            ret, frame = capture.read()
            if ret is True:
                self._queue.put(frame, block=True)
            else:
                break

