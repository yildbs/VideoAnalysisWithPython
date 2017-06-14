import cv2
import threading
import numpy as np
import queue
import frame_viewer
import frame_buffer
import object_list
import cnn_for_human_detection


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
        self._rects_output = queue.Queue(300)
        self._frame_buffer = frame_buffer.FrameBuffer(300)
        self._enabled = True
        #self._diff = DifferentiateFrame()
        self._current_count = 0

        self._finder = FindPedestrian(self._frame_buffer, self._rects_output)
        self._finder.start()

        self._viewer_frame = frame_viewer.FrameViewer()
        self._viewer_frame.set_interval(33)
        self._viewer_frame.start()
        self._object_list = object_list.ObjectList()

    def run(self):
        cnn = cnn_for_human_detection.CnnForHumanDetection()
        cnn.initialize([128, 128, 1])

        count_updated = 0
        count_consume = 0
        finder_image_index = 0
        reference_rects = []
        next_reference_rects = []
        while self._enabled is True:
            data = self._frame_buffer.pop_front()
            count_consume, frame = data[0], data[1]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            print('count_consume : ', count_consume)

            while count_consume >= finder_image_index:
                data = self._rects_output.get(block=True)
                finder_image_index, rects = data[0], data[1]
                reference_rects = next_reference_rects
                next_reference_rects = rects
                count_updated = 0

            refined_rects = []
            for (x, y, w, h) in reference_rects:
                refined_rects.append([x, y, x+w, y+h])

            self._object_list.push(count_consume, refined_rects)
            object_list = self._object_list.get_object_list()
            for obj in object_list:
                print('')
                x, y, x2, y2 = obj.get_rect()
                roi = gray[x:x2, y:y2]
                #roi = frame(obj.get_rect())

                cnn.predict(roi)



            line_width = 20 - count_updated
            if line_width <= 2:
                line_width = 2

            type_rects, distances, scores = self._object_list.get_rects_with_type()

            index = 0
            for type_rect in type_rects:
                type = type_rect[0]
                rect = type_rect[1]
                (x, y, x2, y2) = rect
                color = []
                if type == object_list.ObjectList.ObjectType.HUMAN:
                    color = (255, 255, 255)
                elif type == object_list.ObjectList.ObjectType.ETC:
                    color = (0, 255, 0)
                cv2.rectangle(frame, (x, y), (x2, y2), color, line_width)
                cv2.putText(frame, str(index) + ':' + str(int(distances[index])) + ':' + str(int(scores[index])), (x, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1.0, color, 5)
                index = index + 1

            self._viewer_frame.push_frame(frame)

            count_updated = count_updated + 1
            print('count_updated : ', count_updated)

    def set_enabled(self, enabled):
        self._enabled = enabled

    def push(self, item, block=True):
        self._frame_buffer.push([self._current_count, item])
        self._current_count = self._current_count + 1


class FindPedestrian(threading.Thread):
    def __init__(self, frame_buffer, rects_output):
        threading.Thread.__init__(self)
        self._frame_buffer = frame_buffer
        self._rects_output = rects_output
        self._enabled = True
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def set_enabled(self, enabled):
        self._enabled = enabled

    def run(self):
        while self._enabled is True:
            data = self._frame_buffer.get_latest()
            frame_count, frame = data[0], data[1]
            rects, weights = self._hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
            self._rects_output.put([frame_count, rects], block=True)
            print('hog: ', len(rects))

