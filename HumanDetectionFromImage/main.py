import cv2
import glob
import os
import random


def save_human(rects, frame, file_name):
    cnt = 0
    for (x, y, w, h) in rects:
        roi = frame[y:y + w * 2 - 2, x:x + w - 1, ]
        cv2.imwrite(file_name + '_' + str(cnt) + '.jpg', roi)
        cnt = cnt + 1


def save_not_human(rects, frame, file_name):
    cnt = 0
    if len(rects) == 0:
        width, height, _ = frame.shape
        w = int(random.random() * 99999)
        min = int(height / 6)
        max = int(height / 2)
        w = w % (max-min) + min
        roi = frame[0:w * 2 - 2, 0:w - 1, ]
        cv2.imwrite(file_name + '_' + str(cnt) + '.jpg', roi)
        cnt = cnt + 1


if __name__ == "__main__":
    print("Start!")

    search_path = '/home/yildbs/Data/danusys_dataset_all/'
    save_path = '/home/yildbs/Data/danusys_dataset_all_refined/'

    directory_list = []
    directory_list.append('output_101-6_afternoon_20170324162100_20170324171700_1')
    directory_list.append('output_101-6_afternoon_20170324162100_20170324171700_2')
    directory_list.append('output_101-6_afternoon_20170324162100_20170324171700_3')
    directory_list.append('output_101-6_afternoon_20170324162100_20170324171700_4')
    directory_list.append('output_101-6_afternoon_20170324162100_20170324171700_5')
    directory_list.append('output_101-6_night_20170324204600_20170324212300_1')
    directory_list.append('output_101-6_night_20170324204600_20170324212300_2')
    directory_list.append('output_101-6_night_20170324204600_20170324212300_3')
    directory_list.append('output_101-6_night_20170324204600_20170324212300_4')
    directory_list.append('output_101-6_night_20170324204600_20170324212300_5')
    directory_list.append('output_838-30_afternoon_20170324174800_20170324182500_1')
    directory_list.append('output_838-30_afternoon_20170324174800_20170324182500_2')
    directory_list.append('output_838-30_afternoon_20170324174800_20170324182500_3')
    directory_list.append('output_838-30_afternoon_20170324174800_20170324182500_4')
    directory_list.append('output_94-93_afternoon_20170324143500_20170324153500_1')
    directory_list.append('output_94-93_afternoon_20170324143500_20170324153500_2')
    directory_list.append('output_94-93_afternoon_20170324143500_20170324153500_3')
    directory_list.append('output_94-93_afternoon_20170324143500_20170324153500_4')
    directory_list.append('output_94-93_afternoon_20170324153500_20170324160300_1')
    directory_list.append('output_94-93_afternoon_20170324153500_20170324160300_2')
    directory_list.append('output_94-93_afternoon_20170324153500_20170324160300_3')
    directory_list.append('output_94-93_afternoon_20170324153500_20170324160300_4')
    directory_list.append('output_94-93_night_20170324201100_20170324204900_1')
    directory_list.append('output_94-93_night_20170324201100_20170324204900_2')
    directory_list.append('output_94-93_night_20170324201100_20170324204900_3')
    directory_list.append('output_94-93_night_20170324201100_20170324204900_4')
    directory_list.append('output_sample4')

    image_list = []
    for dir in directory_list:
        image_list.append([dir, glob.glob(search_path+dir+'/*.ppm')])

    directory_human = '1_human/'
    directory_not_human = '2_not_human/'

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    for bundle in image_list:
        dir = bundle[0]
        output_path = save_path + dir + '/'
        output_human_path = output_path + directory_human
        output_not_human_path = output_path + directory_not_human
        os.makedirs(output_human_path, exist_ok=True)
        os.makedirs(output_not_human_path, exist_ok=True)

        image_paths = bundle[1]
        for image in image_paths:
            image_file_name = image[image.rfind('/')+1:image.rfind('.')]

            frame = cv2.imread(image)
            width, height, channels = frame.shape
            if width <= 128 or height <= 128:
                continue

            rects, weights = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)

            # SAVE IMAGES
            save_human(rects, frame, output_human_path + image_file_name)
            save_not_human(rects, frame, output_not_human_path + image_file_name)

