from flask import Flask, jsonify
import sys
import random
import string
import numpy as np
import cv2 as cv
import time

app = Flask(__name__)

#TODO: Medium computations on medium data (e.g., image transformations). 
# A call to execute an instance would take at least 10s of seconds and does not create significant CPU or memory loads.
@app.route('/')
def medium():
    if len(sys.argv) < 2:
        return 'something went wrong!'
    
    img = cv.imread('./Image.jpg', 0)
    rows, cols = img.shape
    M = np.float32([[1, 0, 100], [0, 1, 50]])
    dst = cv.warpAffine(img, M, (cols, rows))
    cv.imshow('img', dst)
    cv.destroyAllWindows()
    time.sleep(10)
    return 'Image transformed \n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8000)
