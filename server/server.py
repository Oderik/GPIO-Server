# !/usr/bin/env python

from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer
from string import Template
import cgi
from urlparse import urlparse

from light import Light


class IlluminationHandler(SimpleHTTPRequestHandler):
    light = Light()

    with open("status.html", "r") as template_file:
        template = Template(template_file.read())

    def format_light_status(self):
        if IlluminationHandler.light.state():
            return "an"
        else:
            return "aus"

    def address_string(self):
        return self.client_address

    def respond_status(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(IlluminationHandler.template.safe_substitute(dict(led_status=self.format_light_status())))

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
                IlluminationHandler.light.toggle()

            self.respond_status()
        except IOError:
            self.send_error(500, 'There went what not')


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
