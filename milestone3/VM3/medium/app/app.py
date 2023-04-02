from flask import Flask, jsonify
import sys
import string
import numpy as np
import cv2 as cv
import time

app = Flask(__name__)

@app.route('/medium/app')
def medium():
    if len(sys.argv) < 2:
        return 'something went wrong!'

    ''' code modified from https://www.geeksforgeeks.org/image-transformations-using-opencv-in-python/ '''

    img = cv.imread('./Image.JPG', 0)
    rows, cols = img.shape
    M = np.float32([[1, 0, 100], [0, 1, 50]])
    dst = cv.warpAffine(img, M, (cols, rows))
    time.sleep(10)
    return 'Image transformed by: ' + sys.argv[1] + '\n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5200)
