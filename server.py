from BaseHTTPServer import BaseHTTPRequestHandler
import SocketServer
from string import Template
import cgi

import pingo


class IlluminationHandler(BaseHTTPRequestHandler):
    print "Initializing"
    board = pingo.detect.MyBoard()
    if board is None:
        board = pingo.ghost.GhostBoard()
    pin = board.pins[8]
    pin.mode = pingo.OUT
    pin.lo()
    template = Template(open("status.html", "r").read())

    def format_light_status(self):
        if self.pin.state == pingo.HIGH:
            return "an"
        else:
            return "aus"

    def respond_status(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.template.safe_substitute(dict(led_status=self.format_light_status())))

    def do_GET(self):
        try:
            if self.path.endswith("toggle"):
                self.toggle_light()
            if not self.path.endswith("favicon.ico"):
                self.respond_status()
            else:
                self.send_response(200, "OK")
        except IOError:
            self.send_error(404, 'File Not Found')


    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                })
            if form.getvalue("action") == "toggle":
                self.toggle_light()

            self.respond_status()
        except IOError:
            self.send_error(500, 'There went what not')


    def toggle_light(self):
        pin = self.pin
        if pin.state == pingo.LOW:
            pin.hi()
        else:
            pin.lo()


def main():
    server = SocketServer.TCPServer(("", 8081), IlluminationHandler)

    try:
        print('Server started.')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down.')
        server.socket.close()


if __name__ == '__main__':
    main()
