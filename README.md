# CPU Load Monitoring App

This simple app can be used to monitor your machine's CPU load and uptime.

## Python Dependencies
* [uptime](http://pythonhosted.org//uptime/)
* [flask](http://flask.pocoo.org/docs/0.10/)

## To Run
1. Start Monitor process.
  * `python monitor.py`
2. Start Flask server.
  * `python flask/server.py`
3. Open http://localhost:5000/ in your browser.

## To Run Unit Tests
`python test.py`

## Design
![Design](https://raw.githubusercontent.com/domoench/load-monitor/master/flask/static/design.png?token=ACbj6MViB_qLH_KX4qgDV7JfqYQrS1Bhks5UZRISwA%3D%3D)

## Other Citations
* [Mike Bostock's D3 Tutorial](http://bost.ocks.org/mike/bar/3/)
* [d3.js](d3js.org)
