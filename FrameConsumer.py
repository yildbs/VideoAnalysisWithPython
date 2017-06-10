import cv2
import threading


class BackgroundFrame():
    def __init__(self, ratio):
        self._frame = []
        self._count = 0
        self._ratio = ratio

    def push(self, frame):
        if self._count is 0:
            self._frame = frame.copy()
        else:
            a = self._frame * (1.0 - self._ratio)
            b = frame * self._ratio
            self._frame = a + b
            #self._frame = self._frame * (1.-self._ratio) + frame * self._ratio
            #self._frame = frame.copy()
        self._count = self._count + 1

    def get_frame(self):
        return self._frame


class DifferentiateFrame():
    def __init__(self):
        self._diff = []
        self._background = BackgroundFrame(0.05)

    def push(self, frame):
        self._background.push(frame)
        frame = frame * 1.0

        self._diff = frame - self.get_background()
        self._diff = abs(self._diff)

    def get_diff(self):
        return self._diff

    def get_background(self):
        return self._background.get_frame()


class FrameConsumer(threading.Thread):

    def __init__(self, input_frame_queue):
        threading.Thread.__init__(self)
        self.input_frame_queue = input_frame_queue
        self._enabled = True
        self._diff = DifferentiateFrame()

    def run(self):
        while self._enabled is True:
            frame = self.input_frame_queue.get(block=True)
            self._diff.push(frame)

            cv2.imshow('background', self._diff.get_background() / 255.)
            cv2.imshow('diff', self._diff.get_diff() / 255.)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

    def set_enabled(self, enabled):
        self._enabled = enabled
