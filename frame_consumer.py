import cv2
import threading
import numpy as np
import queue
import time
import frame_buffer


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

    def __init__(self):
        threading.Thread.__init__(self)
        # self._frame_buffer = queue.Queue(100)
        self._rects_output = queue.Queue(100)
        self._frame_buffer = frame_buffer.FrameBuffer(30)
        self._enabled = True
        self._diff = DifferentiateFrame()
        #self._consume_count = 0
        self._current_count = 0
        self._reference_rects = []

        #self._finder_image_index = 0
        self._finder = FindPedestrian(self._frame_buffer, self._rects_output)
        self._finder.start()

    def run(self):
        count_updated = 0
        count_consume = 0
        finder_image_index = 0
        while self._enabled is True:
            if count_consume >= finder_image_index:
                data = self._rects_output.get(block=True)
                finder_image_index, rects = data[0], data[1]
                #finder_image_index, rects = self._rects_output.get(block=True)
                #finder_image_index = frame_count
                self._reference_rects = rects
                count_updated = 0
            data = self._frame_buffer.pop_front()
            count_consume, frame = data[0], data[1]

            line_width = 20 - count_updated
            if line_width <= 2:
                line_width = 2

            print(count_consume, len(self._reference_rects))
            for (x, y, w, h) in self._reference_rects:
                cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), line_width)

            #gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            #self._diff.push(gray)
            #cv2.imshow('background', self._diff.get_background() / 255.)
            #cv2.imshow('diff', self._diff.get_diff())
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

            count_updated = count_updated + 1
            #count_consume = count_consume + 1

    def set_enabled(self, enabled):
        self._enabled = enabled

    def push(self, item, block=True):
        '''
                if self._finder.is_running() is False:
            self._reference_rects = self._finder.get_rects()
            self._finder = FindPedestrian(self._hog, item)
            self._finder.start_running()
            self._finder.start()
            self._finder_image_index = self._current_count
            try:
                print('bbbb try')
                self._lock_updated.acquire()
                self._updated = True
                print('bbbb acquire')
            finally:
                self._lock_updated.release()
                print('bbbb release')
        :param item: 
        :param block: 
        :return: 
        '''

        #else:
            #print('a')
        #self._frame_buffer.put(item, block)
        self._frame_buffer.push([self._current_count, item])
        self._current_count = self._current_count + 1

        여기 가문제인것같다!!!!!!!!!!!!!!!!!!!1
        push하면 서값 이씹히는 거확인하 기current_count 가이


상
class FindPedestrian(threading.Thread):
    def __init__(self, buffer, rects_output):
        threading.Thread.__init__(self)
        self._buffer = buffer
        self._rects_output = rects_output

        self._enabled = True
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        self._updated = False
        self._lock_updated = threading.Lock()

    def set_enabled(self, enabled):
        self._enabled = enabled

    def _set_updated(self, value):
        try:
            self._lock_updated.acquire()
            self._updated = value
        finally:
            self._lock_updated.release()

    def is_updated(self):
        if self._updated is False:
            return False
        self._set_updated(False)
        return True

    def run(self):
        while self._enabled is True:
            data = self._buffer.get_latest()
            frame_count, frame = data[0], data[1]
            rects, weights = self._hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
            self._rects_output.put([frame_count, rects], block=True)
            self._set_updated(True)

