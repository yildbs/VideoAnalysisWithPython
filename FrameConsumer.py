import cv2
import threading
import numpy as np


class BackgroundFrame():
    def __init__(self, ratio):
        self._frame = np.zeros(0)
        self._count = 0
        self._ratio = ratio

    def push(self, frame):
        if self._count is 0:
            self._frame = frame.copy()
        else:
            self._frame = self._frame * (1.-self._ratio) + frame * self._ratio

        self._count = self._count + 1

    def get_frame(self):
        return self._frame


class DifferentiateFrame():
    def __init__(self):
        self._diff = np.zeros(0)
        self._background = BackgroundFrame(0.005)

    def push(self, frame):
        frame = frame * 1.0
        self._background.push(frame)

        diff = frame - self.get_background()
        diff = np.absolute(diff)
        diff = cv2.convertScaleAbs(diff)

        edstring = 'e5ed3'
        current = edstring[0]
        kernel_size = 3
        for c in edstring[1:]:
            if c is 'e' or c is 'd':
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                if current is 'd':
                    diff = cv2.dilate(diff, kernel)
                else:
                    diff = cv2.erode(diff, kernel)
                kernel_size = 3
                current = c
            else:
                kernel_size = int(c)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        diff = cv2.erode(diff, kernel)

        ret, diff = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)
        #diff = cv2.adaptiveThreshold(diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, 0)

        diff, contours, hierarchy = cv2.findContours(diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(diff, contours, -1, (0, 255, 0), 3)

        self._diff = diff

    def get_diff(self):
        return self._diff

    def get_background(self):
        return self._background.get_frame()


class FrameConsumer(threading.Thread):

    def __init__(self, input_frame_queue):
        threading.Thread.__init__(self)
        self._input_frame_queue = input_frame_queue
        self._enabled = True
        self._diff = DifferentiateFrame()

    def run(self):
        while self._enabled is True:
            frame = self._input_frame_queue.get(block=True)
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            self._diff.push(gray)

            cv2.imshow('background', self._diff.get_background() / 255.)
            cv2.imshow('diff', self._diff.get_diff())
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

    def set_enabled(self, enabled):
        self._enabled = enabled


class FindPedestrian(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._input_frame_queue = input_frame_queue
        self._enabled = True

    def set_enabled(self, enabled):
        self._enabled = enabled

    def run(self):
        while self._enabled is True:
            frame = self._input_frame_queue.get(block=True)