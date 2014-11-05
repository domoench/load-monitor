from flask import Flask, render_template
import json
app = Flask(__name__)

DATA_PATH = '../data.json'

@app.route('/', methods = ['GET'])
def index_route(name='index'):
  return render_template('index.html', name=name)

@app.route('/state', methods = ['GET'])
def state_route(name='state'):
  with open(DATA_PATH, 'r') as f:
    data = json.load(f)
    return json.dumps(data)

if __name__ == '__main__':
  app.debug = True
  app.run()
