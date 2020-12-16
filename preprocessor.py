import math
import numpy as np
import cv2 as cv


def process(img):
    pt_center = (math.ceil(img.shape[0]/2), math.ceil(img.shape[1]/2))

    img_resized = cv.resize(img, pt_center)

    points = get_points(img_resized.copy())

    warped = four_point_transform(img_resized, points)

    aspect_ratio = warped.shape[1]/warped.shape[0]

    warped_resized = cv.resize(warped, (400, 400/aspect_ratio))

    return warped_resized


def get_points(img):
    denoised_img = cv.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    gray = cv.cvtColor(denoised_img, cv.COLOR_BGR2GRAY)

    mask = cv.inRange(gray, 190, 255)
    res = cv.bitwise_and(gray, gray, mask=mask)

    kernel = np.ones((5, 5), np.uint8)

    dilated = cv.dilate(res, kernel, iterations=5)
    eroded = cv.erode(dilated, kernel, iterations=1)

    _, bw_image = cv.threshold(
        eroded,
        200,
        255,
        cv.THRESH_BINARY+cv.THRESH_OTSU
    )

    edges = cv.Canny(bw_image, 50, 100, None, 3)

    contours, hierarchy = cv.findContours(
        edges,
        cv.RETR_EXTERNAL,
        cv.CHAIN_APPROX_SIMPLE
    )

    roi = max_area_contour(contours)

    print(approximate_contour(roi)[:, 0, :])

    return approximate_contour(roi)[:, 0, :]


def approximate_contour(cnt):
    epsilon = 0.03*cv.arcLength(cnt, True)
    return cv.approxPolyDP(cnt, epsilon, True)


def order_points(pts):
    xSorted = pts[np.argsort(pts[:, 0]), :]

    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost

    return np.array([tl, tr, br, bl], dtype="float32")


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def max_area_contour(contours):
    max_contour = None
    max_area = -1

    for contour in contours:
        area = cv.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    return max_contour
