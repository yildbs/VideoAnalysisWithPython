import cv2
import glob



hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

'''
file_list = glob.glob('../Data/INRIA/Train_original/pos/*')
for path in file_list:
    frame = cv2.imread(path)
    rects, weights = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 10)

    cv2.imshow('frame', frame)
    cv2.waitKey(10)
'''


video_file_name = '../Videos/sample.avi'
capture = cv2.VideoCapture(video_file_name)

while True:
    ret, frame = capture.read()
    if ret is True:

        rects, weights = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 10)

        cv2.imshow('frame', frame)
        cv2.waitKey(1)

    else:
        break