import socket

target_host = "0.0.0.0"
target_port = 9999
get_size = 4096
message = "GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n"

# build a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# make a connect
address_object = (target_host, target_port)
client.connect(address_object)

# send some data
client.send(message)

# get data
response = client.recv(get_size)

print "these are the responses:"
print ">>>>>>>>>>>>>>"

print response

client.close()