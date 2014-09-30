#!/usr/bin/env python

from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
from string import Template
import cgi
from urlparse import urlparse

import pingo

class IlluminationHandler(SimpleHTTPRequestHandler):
    print "Initializing"
    board = pingo.detect.MyBoard()
    if board is None:
        board = pingo.ghost.GhostBoard()
        pin = board.pins[8]
    else:
        pin = board.pins[23]

    pin.mode = pingo.OUT
    pin.lo()
    template_file = open("status.html", "r")
    template = Template(template_file.read())
    template_file.close()

    def format_light_status(self):
        if self.pin.state == pingo.HIGH:
            return "an"
        else:
            return "aus"

    def address_string(self):
        return self.client_address

    def respond_status(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.template.safe_substitute(dict(led_status=self.format_light_status())))

    def do_GET(self):
        try:
            parse_result = urlparse(self.path)
            if parse_result.path.endswith(".py"):
                self.send_error(403)
                return
            if parse_result.path.endswith("status.html") or parse_result.path == "/":
                self.respond_status()
                return
        except IOError:
            self.send_error(404)
        return SimpleHTTPRequestHandler.do_GET(self)


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
