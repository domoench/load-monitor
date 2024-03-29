## CPU Load Monitoring App

A simple app to monitor and visualize your machine's CPU load and uptime.

### Dependencies
Python:
* [uptime](http://pythonhosted.org//uptime/)
* [flask](http://flask.pocoo.org/docs/0.10/)

JS:
* [jQuery](https://api.jquery.com/)
* [d3.js](d3js.org)
* [d3-tip](https://github.com/Caged/d3-tip/blob/master/examples/bars.html)

### To Run
1. Start Monitor process.
  * `python monitor.py`
2. Start Flask server (in a separate terminal window).
  * `cd flask/`
  * `python server.py`
3. Open http://localhost:5000/ in your browser.

I run this all in a virtualenv python environment with Python 2.7.8.

### To Run Unit Tests
`python test.py`

### Design
![Design](https://raw.githubusercontent.com/domoench/load-monitor/master/flask/static/design.png?token=ACbj6MViB_qLH_KX4qgDV7JfqYQrS1Bhks5UZRISwA%3D%3D)

### Other Citations
* [Mike Bostock's D3 Tutorial](http://bost.ocks.org/mike/bar/3/)
