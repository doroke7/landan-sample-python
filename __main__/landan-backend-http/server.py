# src/pk_studio_reader_ir/server.py

from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"PK Studio Reader IR Server")


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), Handler)

    print("Server started at http://0.0.0.0:8080")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.server_close()


if __name__ == "__main__":
    main()