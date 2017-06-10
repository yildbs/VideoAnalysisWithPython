import cv2
import threading
import time


class FrameProducer(threading.Thread):

    def __init__(self, file_name, consumer):
        threading.Thread.__init__(self)
        self._file_name = file_name
        self._consumer = consumer

    def run(self):
        capture = cv2.VideoCapture(self._file_name)

        while True:
            ret, frame = capture.read()
            if ret is True:
                print('push!')
                self._consumer.push(frame, True)
                time.sleep(0.03)
            else:
                break

