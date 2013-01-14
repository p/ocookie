import bottle
import threading
import socket
import time as _time

app = bottle.Bottle()

@app.route('/')
def no_cookies():
    return 'none'

@app.route('/set')
def set_cookie():
    bottle.response.set_cookie('visited', 'yes')
    return 'success'

# server starting

def start_bottle_server(app, port, **kwargs):
    server_thread = ServerThread(app, port, kwargs)
    server_thread.daemon = True
    server_thread.start()
    
    ok = False
    for i in range(10):
        try:
            conn = socket.create_connection(('127.0.0.1', port), 0.1)
            ok = True
        except socket.error as e:
            _time.sleep(0.1)
        if ok:
            conn.close()
            break
    if not ok:
        import warnings
        warnings.warn('Server did not start after 1 second')

class ServerThread(threading.Thread):
    def __init__(self, app, port, server_kwargs):
        threading.Thread.__init__(self)
        self.app = app
        self.port = port
        self.server_kwargs = server_kwargs
    
    def run(self):
        bottle.run(self.app, host='localhost', port=self.port, **self.server_kwargs)

def run(port):
    start_bottle_server(app, port)
