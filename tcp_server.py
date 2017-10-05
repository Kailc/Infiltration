import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999
max_conn = 5
recv_size = 4096


def handle_client(client_socket):

    request = client_socket.recv(recv_size)
    print "[*] Received: %s" % request

    client_socket.send("ACK!")

    client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address_object = (bind_ip, bind_port)
server.bind(address_object)

server.listen(max_conn)

print "[*] Listening on %s:%d" % address_object

while True:
    client, addr = server.accept()

    print "[*] Accepted connection from %s:%d" % (addr[0], addr[1])

    client_threading = threading.Thread(target=handle_client, args=(client,))
    client_threading.start()