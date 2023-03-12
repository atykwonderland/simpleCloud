from flask import Flask, jsonify
import sys
import random
import string

app = Flask(__name__)

@app.route('/')
def light():
    if len(sys.argv) < 2:
        return 'something went wrong!'
    letters = string.ascii_letters
    rand_string = ''.join(random.choice(letters) for i in range(10))
    return 'Hello ' + rand_string + ' from: ' + sys.argv[1] + '! \n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8000)