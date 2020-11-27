from socket import socket, AF_INET, SOCK_STREAM

HOST = '127.0.0.1'
PORT = 1337


routes = {
    "/test": "test.html",
    "/index": "index.html",
    "/": "index.html"
}


def send_response(send_socket, initial_header, message_body):
    final_packet = initial_header + 'Content-Type: text/html\n\n' + message_body
    send_socket.send(final_packet.encode())
    send_socket.close()


def get_file_data(name):
    f = open(name)
    file = f.read()
    f.close()
    return file


server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    connectionSocket, address = server_socket.accept()
    print('Connection from', address)

    message = connectionSocket.recv(1024)

    split_message = message.decode().split()
    method = split_message[0]
    filename = split_message[1]

    header = ""
    body = ""

    if method != "GET":
        # Given url is in our set of routes
        print("Could not serve: {}".format(filename))
        body = get_file_data("400_bad_request.html")
        header = 'HTTP/1.1 400 Bad Request\n'

    elif filename in routes.keys():
        # Given url is in our set of routes
        print("Serving: {}".format(filename))
        body = get_file_data(routes[filename])
        header = 'HTTP/1.1 200 OK\n'

    else:
        # Given url is not within our set of routes
        print("Could not serve: {}".format(filename))
        body = get_file_data("404_not_found.html")
        header = 'HTTP/1.1 404 Not Found\n'

    send_response(connectionSocket, header, body)
