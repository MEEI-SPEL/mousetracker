import cv2
import numpy as np


def __show_debug_image(name, frame):
    return
    cv2.imshow(name, frame)
    cv2.waitKey()


def process_frame(frame):
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    __show_debug_image('original', frame_hsv)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(frame_hsv, lower_red, upper_red)
    lower_red1 = np.array([170, 50, 50])
    upper_red1 = np.array([180, 255, 255])
    mask1 = cv2.inRange(frame_hsv, lower_red1, upper_red1)
    mask = mask0 + mask1
    output_img = frame_hsv.copy()
    output_img[np.where(mask == 0)] = 0
    output_grey = cv2.cvtColor(output_img, cv2.COLOR_BGR2GRAY)

    # output_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # _, _, output_grey = cv2.split(frame)

    __show_debug_image('grey', output_grey)
    ret, thresh1 = cv2.threshold(output_grey, 150, 255,
                                 cv2.THRESH_OTSU)
    __show_debug_image('thresholded', thresh1)
    # the value of 15 is chosen by trial-and-error to produce the best outline of the skull
    kernel = np.ones((2, 2), np.uint8)
    # square image kernel used for erosion
    erosion = cv2.erode(thresh1, kernel, iterations=2)
    # refines all edges in the binary image

    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE,
                               kernel)  # this is for further removing small noises and holes in the image
    __show_debug_image('processed', closing)
    return closing.size, np.count_nonzero(closing)


if __name__ == "__main__":
    thisframe = cv2.imread('first.png')
    process_frame(thisframe)
