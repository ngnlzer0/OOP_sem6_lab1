from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 7200
HOST = '0.0.0.0'

class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        response = (
            '<html><head><title>Простий HTTP-сервер</title></head>'
            '<body>Був отриманий GET-запит.</body></html>'
        )
        self.wfile.write(response.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Handler):
    server_address = (HOST, PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущено на http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер зупинено.")
        httpd.server_close()


if __name__ == "__main__":
    run()