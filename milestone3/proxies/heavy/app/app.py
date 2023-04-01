from flask import Flask, jsonify
import sys
import random
import string
import cv2
import numpy as np
import time

app = Flask(__name__)

@app.route('/heavy/app')
def heavy():

    if len(sys.argv) < 2:
        return 'something went wrong!'

    ''' code modified from https://www.geeksforgeeks.org/perspective-transformation-python-opencv/ '''

    # load a file
    cap = cv2.VideoCapture("/home/comp598-user/milestone2/heavy/app/EARTH.mp4")
    if not cap.isOpened(): print("ERROR opening the file!")


    while True:

        _, frame = cap.read()
        if not np.any(frame): break
        
        # Locate points of the image which you want to transform
        pts1 = np.float32([[0, 100], [100, 100],
                           [0, 200], [100, 200]])
        pts2 = np.float32([[0, 0], [200, 0],
                           [0, 300], [200, 300]])

        # Apply Perspective Transform Algorithm
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        
        result = cv2.warpPerspective(frame, matrix, (np.shape(matrix)[0], np.shape(matrix)[1]))

    cap.release()
    time.sleep(100)
    
    return 'Video transformed by: ' + sys.argv[1] + '\n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)