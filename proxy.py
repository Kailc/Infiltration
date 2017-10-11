
#coding=utf-8
import sys
import socket
import threading

# 本地请求远端的处理
def request_handler(buffer):

    return buffer

# 远端响应本地的处理
def response_handler(buffer):

    return buffer


# 将数据src转为特定格式显示
def hexdump(src, length=16):

    result = []
    # unicode编码为4个字节，其余为2个字节
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i : i + length]
        # 转为16进制字符
        hexa = b' '.join(["%0*X" %(digits, ord(x)) for x in s])
        # 控制字符转为'.'，其余照样
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        # %-*s 代表输入一个字符串，-号代表左对齐、后补空白，*号代表对齐宽度由length * (digits + 1)确定
        result.append(b"%04X    %-*s    %s" %(i, length * (digits + 1), hexa, text))

    print b'\n'.join(result)

def receive_from(connection):

    buffer = ""

    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)

            if not data:
                break

            buffer += data
    except:
        pass

    return buffer

def proxy_handler(client_socket, remote_host, remost_port, receive_first):

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    remote_socket.connect((remote_host, remost_port))

    if receive_first:

        # 接收远端数据，并显示
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # 远端响应
        remote_buffer = response_handler(remote_buffer)

        # 将远端的响应结果发送至本地
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost. " % len(remote_buffer)
            client_socket.send(remote_buffer)

    while True:

        # 接收本地请求数据
        local_buffer = receive_first(client_socket)

        if len(local_buffer):

            # 显示本地请求数据
            print "[==>] Received %d bytes from localhost. " % len(local_buffer)
            hexdump(local_buffer)

            # 处理本地请求
            local_buffer = request_handler(local_buffer)

            # 向远端发送本地请求结果
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote ."

        # 接受远端数据
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):

            # 显示远端数据
            print "[<==] Received %d bytes from remote . " % len(remote_buffer)
            hexdump(remote_buffer)

            # 处理远端响应
            remote_buffer = response_handler(remote_buffer)

            # 发送远端响应处理结果至本地
            client_socket.send(remote_buffer)

            print "[<==] Sent to localhost. "


        # 在两边均无数据发送时，关闭连接
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print "[*] No more data. Closing cnnections. "

            break



def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host, local_port)
        print "[!!] Check for other listening sockets or correct permissions. "
        sys.exit(0)

    print "[*] Listening on %s:%d" % (local_host, local_port)


    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print "[==>] Received incoming connection from %s:%d" % (addr[0], addr[1])

        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,remote_host,remote_port,receive_first))

        proxy_thread.start()

def do_main():


    if len(sys.argv[1:]) != 5:
        print "Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        print "Example: ./proxy.py 127.0.0.1 8080 10.10.10.10 8080 True"
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "true" in receive_first.lower():
        receive_first = True
    else:
        receive_first = False

