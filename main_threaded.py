from socket import socket, AF_INET, SOCK_STREAM, gethostname
import os
from time import strptime, mktime
import threading

HOST = gethostname()
PORT = 1337

routes = {
    "/test": "test.html",
    "/index": "index.html",
    "/": "index.html"
}

media = {
    "/favicon.ico": "favicon.ico"
}

def get_file_data(name):
    f = open(name, 'rb')
    file = f.read()
    f.close()
    return file


def handle_data(file_name, message, format):

    print("File to serve: {}".format(file_name))
    print("Message: {}".format(message))
    print("File format: {}".format(format))
    print()

    header_template = "HTTP/1.1 {}\r\n"
    content_type_template = 'Content-Type: {}\r\nContent-Length: {}\r\n\r\n'

    if file_name:
        body = get_file_data(file_name)
    else:
        body = b""

    header = header_template.format(message).encode()

    if format:
        content_type = content_type_template.format(format, str(len(body))).encode()
    else:
        content_type = b""

    return header + content_type + body

def threaded(my_socket):
    print("Thread with id {} created".format(threading.get_ident()))
    # Will contain the final response
    data = b""

    try:
        message = my_socket.recv(1024)

        split_message = message.decode().split("\r\n")
        first_line = split_message[0].split()
        method = first_line[0]
        filename = first_line[1]

        output = {}

        for field in split_message:
            pair = field.split(":")
            if len(pair) >= 2:
                output[pair[0].strip()] = ":".join(pair[1:]).strip()

        # 400 - handle incorrect method
        if method != "GET":
            # Given url is in our set of routes
            print("Could not serve: {}".format(filename))
            data = handle_data("400_bad_request.html", '400 Bad Request', 'text/html')

        # 200 - handle known routes
        elif filename in routes.keys():
            # Given url is in our set of routes
            print("Serving: {}".format(filename))
            if "If-Modified-Since" in output:
                mod_since = mktime(strptime(output["If-Modified-Since"], "%a, %d %b %Y %I:%M:%S %Z"))
                file_mod = os.path.getmtime(routes[filename])
                if mod_since < file_mod:
                    # 304 - Not Modified
                    data = handle_data("", '304 Not Modified', "")
                else:
                    data = handle_data(routes[filename], '200 OK', 'text/html')
            else:
                data = handle_data(routes[filename], '200 OK', 'text/html')

        # 200 - handle media
        elif filename in media.keys():
            print("Serving: {}".format(filename))
            if "If-Modified-Since" in output:
                mod_since = mktime(strptime(output["If-Modified-Since"], "%a, %d %b %Y %I:%M:%S %Z"))
                file_mod = os.path.getmtime(media[filename])
                if mod_since < file_mod:
                    # 304 - Not Modified
                    data = handle_data("", '304 Not Modified', "")
                else:
                    data = handle_data(media[filename], '200 OK', 'image/x-icon')
            else:
                data = handle_data(media[filename], '200 OK', 'image/x-icon')

        # 404 - handle not found
        else:
            # Given url is not within our set of routes
            print("Could not serve: {}".format(filename))
            data = handle_data("404_not_found.html", '404 Not Found', 'text/html')

    except socket.timeout:
        # 408 - handle timeout
        print("Could not serve: timeout")
        data = handle_data("408_request_timed_out.html", '408 Request Timed Out', 'text/html')

    finally:
        # print(data)
        connectionSocket.send(data)
        connectionSocket.close()

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    connectionSocket, address = server_socket.accept()
    print('Connection from', address)

    connectionSocket.settimeout(10)

    threading.Thread(target=threaded, args=(connectionSocket,)).start()

server_socket.close()