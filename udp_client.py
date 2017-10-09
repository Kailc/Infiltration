# 运行该代码前需要先在对方运行UDP服务端代码
# 本脚本中的对方为127.0.0.1（本地主机）
# 可在终端运行：nc -ulp port




import socket



target_host = "127.0.0.1"
target_port = 1234
data_size = 4096
message  = "AAABBBCCC"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address_object = (target_host, target_port)
client.sendto(message, address_object)

data, addr = client.recvfrom(data_size)

print "this is the data:"
print data

print ">>>>>>>>>>>"

print "this is the addr"
print addr