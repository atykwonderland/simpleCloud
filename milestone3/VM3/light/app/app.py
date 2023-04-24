from flask import Flask
import sys

app = Flask(__name__)

@app.route('/light/app')
def light():
    if len(sys.argv) < 2:
        return 'something went wrong!'

    x = 10
    for i in range(20):
        x - x * x
    
    return 'Hello from: ' + sys.argv[1] + '! \n'

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)