import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl
import os

# Specify the path to your SSL certificate and key
CERTIFICATE_PATH = 'certificate.pem'
PRIVATE_KEY_PATH = 'key.pem'
FILES_DIRECTORY = 'files'  # Directory to display files from

class CustomSecureHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # List files in the specified directory
            files = os.listdir(FILES_DIRECTORY)

            # Customize the response to display the list of files with correct download links
            file_list = '\n'.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files])
            response = f'<html><head><title>File List</title></head><body><h1>Files in {FILES_DIRECTORY}:</h1><ul>{file_list}</ul></body></html>'

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            # Serve individual files with Content-Disposition header
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(self.path)}"')
            self.end_headers()

            with open(os.path.join(FILES_DIRECTORY, os.path.basename(self.path)), 'rb') as file:
                self.wfile.write(file.read())

def run_server(host='0.0.0.0', port=5000):
    httpd = HTTPServer((host, port), CustomSecureHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=PRIVATE_KEY_PATH, certfile=CERTIFICATE_PATH, server_side=True)

    print('Starting server on https://{}:{}'.format(host, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Secure File Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address to bind to (default is 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on (default is 5000)')
    args = parser.parse_args()

    run_server(host=args.host, port=args.port)
