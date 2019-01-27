import cv2
import numpy as np
import sys
import pyocr
from PIL import Image

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'

langs = tool.get_available_languages()
print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
# print("Will use lang '%s'" % (self.lang))

def cleanPage(page):
    def resize(img, height=800):
        """ Resize image to given height """
        rat = height / img.shape[0]
        return cv2.resize(img, (int(rat * img.shape[1]), height))

    # Load image and convert it from BGR to RGB
    image = cv2.cvtColor(page, cv2.COLOR_BGR2RGB)
    # Resize and convert to grayscale
    img = cv2.cvtColor(resize(image), cv2.COLOR_BGR2GRAY)
    # Bilateral filter preserv edges
    img = cv2.bilateralFilter(img, 9, 75, 75)
    # Create black and white image based on adaptive threshold
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 4)
    # Median filter clears small details
    img = cv2.medianBlur(img, 11)
    # Add black border in case that page is touching an image border
    img = cv2.copyMakeBorder(img, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    edges = cv2.Canny(img, 200, 250)

    # Getting contours
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Finding contour of biggest rectangle
    # Otherwise return corners of original image
    # Don't forget on our 5px border!
    height = edges.shape[0]
    width = edges.shape[1]
    MAX_COUNTOUR_AREA = (width - 10) * (height - 10)

    # Page fill at least half of image, then saving max area found
    maxAreaFound = MAX_COUNTOUR_AREA * 0.5

    # Saving page contour
    pageContour = np.array([[5, 5], [5, height-5], [width-5, height-5], [width-5, 5]])

    # Go through all contours
    for cnt in contours:
        # Simplify contour
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)

        # Page has 4 corners and it is convex
        # Page area must be bigger than maxAreaFound
        if (len(approx) == 4 and
                cv2.isContourConvex(approx) and
                maxAreaFound < cv2.contourArea(approx) < MAX_COUNTOUR_AREA):

            maxAreaFound = cv2.contourArea(approx)
            pageContour = approx

    def fourCornersSort(pts):
        """ Sort corners: top-left, bot-left, bot-right, top-right """
        # Difference and sum of x and y value
        # Inspired by http://www.pyimagesearch.com
        diff = np.diff(pts, axis=1)
        summ = pts.sum(axis=1)

        # Top-left point has smallest sum...
        # np.argmin() returns INDEX of min
        return np.array([pts[np.argmin(summ)],
                         pts[np.argmax(diff)],
                         pts[np.argmax(summ)],
                         pts[np.argmin(diff)]])


    def contourOffset(cnt, offset):
        """ Offset contour, by 5px border """
        # Matrix addition
        cnt += offset

        # if value < 0 => replace it by 0
        cnt[cnt < 0] = 0
        return cnt


    # Sort and offset corners
    pageContour = fourCornersSort(pageContour[:, 0])
    pageContour = contourOffset(pageContour, (-5, -5))

    # Recalculate to original scale - start Points
    sPoints = pageContour.dot(image.shape[0] / 800)

    # Using Euclidean distance
    # Calculate maximum height (maximal length of vertical edges) and width
    height = max(np.linalg.norm(sPoints[0] - sPoints[1]),
                 np.linalg.norm(sPoints[2] - sPoints[3]))
    width = max(np.linalg.norm(sPoints[1] - sPoints[2]),
                np.linalg.norm(sPoints[3] - sPoints[0]))

    # Create target points
    tPoints = np.array([[0, 0],
                        [0, height],
                        [width, height],
                        [width, 0]], np.float32)

    # getPerspectiveTransform() needs float32
    if sPoints.dtype != np.float32:
        sPoints = sPoints.astype(np.float32)

    # Wraping perspective
    M = cv2.getPerspectiveTransform(sPoints, tPoints)
    newImage = cv2.warpPerspective(image, M, (int(width), int(height)))

    # Saving the result. Yay! (don't forget to convert colors bact to BGR)


    return cv2.cvtColor(newImage, cv2.COLOR_BGR2RGB)


large = cleanPage(cv2.imread('ReceiptSwiss.jpg'))
rgb = cv2.pyrDown(large)
small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(sys.argv[1]), int(sys.argv[2])))
grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

_, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(sys.argv[3]), int(sys.argv[4])))
connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
# using RETR_EXTERNAL instead of RETR_CCOMP
contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#For opencv 3+ comment the previous line and uncomment the following line
#_, contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

mask = np.zeros(bw.shape, dtype=np.uint8)

for idx in range(len(contours)):
    x, y, w, h = cv2.boundingRect(contours[idx])
    mask[y:y+h, x:x+w] = 0
    cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
    r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)

    if r > 0.25 and w > 8 and h > 8:
        boximg=rgb[y:y+h,x:x+w]
        #cv2.imshow('img',boximg)
        line_and_word_boxes = tool.image_to_string(
            Image.fromarray(boximg),
            builder=pyocr.builders.LineBoxBuilder(),
            lang='deu'
        )
        for box in line_and_word_boxes:
            print(f'Box: {box.content}')
        print(line_and_word_boxes)
        cv2.rectangle(rgb, (x, y), (x+w-1, y+h-1), (0, 255, 0), 2)


print(f'Contours: {len(contours)}')
if len(contours) > 0:
    #cv2.imwrite(f'outputs/output_{sys.argv[1]}_{sys.argv[2]}_{sys.argv[3]}_{sys.argv[4]}.png',rgb)
    cv2.imshow('rects', rgb)
    cv2.waitKey(0)
    cv2.destroyAllWindows()