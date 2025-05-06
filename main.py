import http.server
import socketserver
import socket
import os
import re

print("File Bridge by KurXZ")
print("Starting server...")
print("Setting up variables...")
upload_directory = os.getcwd()
defaultPORT = 8000
hostname = socket.getfqdn()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            items = os.listdir(upload_directory)
            list_items = "".join(
                f'<li class=\"p-2 border-b break-words\"><a class=\"text-blue-600 hover:underline\" href=\"/{item}\">{item}</a></li>'
                for item in items
            )

            html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Python File Bridge</title>
    <script src=\"https://cdn.tailwindcss.com\"></script>
</head>
<body class=\"bg-gray-100 font-sans flex flex-col h-screen justify-between\">
    <div class=\"bg-white p-4 rounded shadow\">
        <h1 class=\"text-2xl mb-4\">Folder content</h1>
        <ul class=\"mb-4\">{list_items}</ul>
        <form action=\"/upload\" method=\"post\" enctype=\"multipart/form-data\">
            <label class=\"block mb-2\">Select file to upload:</label>
            <input type=\"file\" name=\"file\" class=\"block mb-4\" required>
            <button type=\"submit\" class=\"px-4 py-2 bg-blue-500 text-white rounded\">Upload</button>
        </form>
    </div>
   
<footer class="shadow-sm mt-2 bg-gray-800 w-full">
    <div class="w-full p-4 flex flex-col lg:flex-row items-center lg:justify-between">
      <span class="text-sm text-gray-500 sm:text-center dark:text-gray-400"><a href="https://github.com/kurxz" class="hover:underline">KurXZ</a> - File Bridge v0.1
    </span>
  <ul class="flex flex-wrap items-center lg:mt-0 mt-1 text-sm font-medium text-gray-500 dark:text-gray-400">   
  <li>
             <a href="https://github.com/kurxz/pyfilebridge/blob/main/README.md" class="hover:underline me-4 md:me-6">About</a>
        </li>
        <li>
            <a href="https://github.com/kurxz/pyfilebridge/blob/main/LICENSE" class="hover:underline me-4 md:me-6">Licensing</a>
        </li>
    </ul>
    </div>
</footer>

</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/upload':
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error(400, "Invalid Content-Type")
                return

            boundary = content_type.split("boundary=")[-1].encode('utf-8')
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)

            parts = data.split(b"--" + boundary)
            for part in parts:
                if b'Content-Disposition' in part:
                    header, filedata = part.split(b"\r\n\r\n", 1)          
                    match = re.search(rb'filename="([^"]+)"', header)
                    if not match:
                        continue
                    filename = os.path.basename(match.group(1).decode('utf-8'))
                    filedata = filedata.rstrip(b"\r\n--")

                    dest_path = os.path.join(upload_directory, filename)
                    with open(dest_path, 'wb') as f:
                        f.write(filedata)

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_error(404, "Not Found")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", defaultPORT), Handler) as httpd:
        print(f"Serving at: {socket.gethostbyname_ex(hostname)[2][1]}:{defaultPORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutting down...")
            httpd.server_close()
