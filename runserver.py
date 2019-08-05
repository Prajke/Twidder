from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketServer
from app import app


http_server = WSGIServer(('127.0.0.1',5000), app, handler_class=WebSocketHandler)
http_server.serve_forever()
