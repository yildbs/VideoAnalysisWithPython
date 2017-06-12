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

        frame_count = 0
        while True:
            start_time = time.time()
            ret, frame = capture.read()
            frame_count = frame_count + 1
            if ret is True:
                print('push!')
                #frame = cv2.resize(frame, (1280, 720))
                self._consumer.push(frame, True)

                elapsed_time = time.time() - start_time
                delay_time = 1/30 - elapsed_time
                if delay_time > 0:
                    time.sleep(1 / 30)
            else:
                break

