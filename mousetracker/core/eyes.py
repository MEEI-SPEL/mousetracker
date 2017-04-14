import cv2
import numpy as np
import attr


@attr.s(frozen=True)
class EyeStats:
    center = attr.ib()
    size = attr.ib()
    angle = attr.ib()
    fitted_area = attr.ib()
    contour_area = attr.ib()


def __show_debug_image(name, frame):
    cv2.imshow(name, frame)
    cv2.waitKey()


def compute_areas(frame)->EyeStats:
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # __show_debug_image('original', frame_hsv)

    output_grey = _red_mask(frame_hsv=frame_hsv)
    thresh1 = _threshold_frame(output_grey)
    closing = _morph_and_smooth(thresh1)
    return contour_to_ellipse(closing)


def contour_to_ellipse(opened):
    _, contours, _ = cv2.findContours(opened, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    largest_contour = max(contours, key=cv2.contourArea)
    center, size, angle = cv2.fitEllipse(largest_contour)
    fitted_area = np.pi * (size[0] / 2) * (size[1] / 2)
    return EyeStats(center=center,
                    size=size,
                    angle=angle,
                    fitted_area=fitted_area,
                    contour_area=cv2.contourArea(largest_contour)
                    )


def _morph_and_smooth(thresh1):
    # the value of 15 is chosen by trial-and-error to produce the best outline of the skull
    kernel = np.ones((3, 3), np.uint8)
    # square image kernel used for erosion
    erosion = cv2.erode(thresh1, kernel, iterations=2)
    # refines all edges in the binary image

    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE,
                               kernel)  # this is for further removing small noises and holes in the image
    # todo: improve this to join large blobs (in case of eyebrow occlusion)
    # __show_debug_image('processed', closing)
    return closing


def _threshold_frame(output_grey):
    ret, thresh1 = cv2.threshold(output_grey, 150, 255,
                                 cv2.THRESH_OTSU)
    # __show_debug_image('thresholded', thresh1)
    return thresh1


def _red_mask(frame_hsv):
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(frame_hsv, lower_red, upper_red)
    lower_red1 = np.array([170, 50, 50])
    upper_red1 = np.array([180, 255, 255])
    mask1 = cv2.inRange(frame_hsv, lower_red1, upper_red1)
    mask = mask0 + mask1
    output_img = frame_hsv.copy()
    output_img[np.where(mask == 0)] = 0

    # __show_debug_image('grey', cv2.cvtColor(output_img, cv2.COLOR_BGR2GRAY))
    return cv2.cvtColor(output_img, cv2.COLOR_BGR2GRAY)


if __name__ == "__main__":
    this_frame = cv2.imread('first.png')
    compute_areas(this_frame)
