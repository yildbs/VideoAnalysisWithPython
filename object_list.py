from enum import Enum


def get_distance_rects(rect1, rect2):
    a_x1, a_y1, a_x2, a_y2 = rect1[0], rect1[1], rect1[2], rect1[3]
    b_x1, b_y1, b_x2, b_y2 = rect2[0], rect2[1], rect2[2], rect2[3]
    dist_1 = 0
    dist_1 += (a_x1 - b_x1) * (a_x1 - b_x1)
    dist_1 += (a_y1 - b_y1) * (a_y1 - b_y1)
    dist_2 = 0
    dist_2 += (a_x2 - b_x2) * (a_x2 - b_x2)
    dist_2 += (a_y2 - b_y2) * (a_y2 - b_y2)

    temp = dist_1 + dist_2

    # TODO Delete the Test Code
    if 0 < temp and temp < 50000:
        print('here')

    return dist_1 + dist_2


class Object:
    def __init__(self, frame_count, rect):
        self._rect_latest = rect
        self._rect_first = rect
        self._frame_index_first = frame_count
        self._frame_index_latest = frame_count
        self._frame_count_advent = 1
        self._frame_count_not_move = 0
        self._frame_count_as_human = 0
        self._is_human = False
        self._updated = False

        # TODO Delete the Test Code
        self.test_distance = 0
        self.test_score = 0

    def is_in(self, rect, distance):
        if get_distance_rects(rect, self._rect_latest) < distance:
            return True
        return False

    def get_frame_index_latest(self):
        return self._frame_index_latest

    def get_rect(self):
        return self._rect_latest

    def update(self, frame_count, rect):
        self._frame_count_advent = self._frame_count_advent + 1

        # TODO Delete the Test Code
        if get_distance_rects(self._rect_latest, rect) != 0:
            self.test_distance = get_distance_rects(self._rect_latest, rect)

        if get_distance_rects(self._rect_latest, rect) < 10:
            self._frame_count_not_move = self._frame_count_not_move + 1
        else:
            self._frame_count_not_move = 0

        # TODO
        self._frame_count_as_human = self._frame_count_as_human + 1

        self._rect_latest = rect
        self._frame_index_latest = frame_count
        self._updated = True

    def is_human(self):
        if not self._updated:
            return self._is_human

        self._updated = False
        score_not_move = self._frame_count_not_move / self._frame_count_advent * -1
        score_as_human = self._frame_count_as_human / self._frame_count_advent
        score = score_not_move*6 + score_as_human*4

        # TODO Delete the Test Code
        self.test_score = score

        if score >= 0:
            self._is_human = True
            return True
        else:
            self._is_human = False
            return False


class ObjectList:
    class ObjectType(Enum):
        HUMAN = 1,
        ETC = 2

    def __init__(self):
        self._object_list = []
        self._frame_width = 0
        self._frame_height = 0
        self._distance_for_same_object = 500

    def push(self, frame_count, rects):
        for rect in rects:
            close_list = []
            for obj in self._object_list:
                if frame_count - obj.get_frame_index_latest() > 100:
                    del obj
                    continue
                if obj.is_in(rect, self._distance_for_same_object) == True:
                    close_list.append(obj)

            if len(close_list) == 0:
                self._object_list.append(Object(frame_count, rect))
            elif len(close_list) == 1:
                for obj in close_list:
                    obj.update(frame_count, rect)
            else:
                #TODO
                for close_obj in close_list:
                    for obj in self._object_list:
                        if close_obj is obj:
                            self._object_list.remove(obj)
                new_obj = Object(frame_count, rect)
                self._object_list.append(new_obj)

    def get_object_list(self):
        return self._object_list

    def get_rects_with_type(self):
        rects = []
        for obj in self._object_list:
            if obj.is_human() == True:
                rects.append([self.ObjectType.HUMAN, obj.get_rect()])
            else:
                rects.append([self.ObjectType.ETC, obj.get_rect()])

        # TODO Delete the Test Code
        distances = []
        scores = []
        for obj in self._object_list:
            distances.append(obj.test_distance)
            scores.append(obj.test_score)

        return rects, distances, scores

    def get_human(self):
        human_list = []
        for obj in self._object_list:
            if obj.is_human() == True:
                human_list.append(obj)
        return human_list

    def get_human_rects(self):
        rects = []
        human_list = self.get_human()
        for human in human_list:
            rects.append(human.get_rect())
        return rects
