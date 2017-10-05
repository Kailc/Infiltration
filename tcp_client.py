import socket

target_host = "www.baidu.com"
target_port = 80
get_size = 4096

# build a socket object
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# make a connect
client.connect((target_host,target_port))

# send some data
client.send("GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n")

# get data
response = client.recv(get_size)

print "these are the responses:"
print ">>>>>>>>>>>>>>"

print response

client.close()