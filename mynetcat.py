#coding=utf-8
import sys
import socket
import getopt
import threading
import subprocess

#定义全局变量

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


#help

def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host - p port"
    print "-l --listen              - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run -execute the given file upon receiving a connection"
    print "-c --command             - initialize a commandshell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples:"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | python ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)


# 发送数据到制定的服务端，并获取服务端的返回数据（如果有的话）
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))

        if len(buffer) > 0:
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response

            buffer = raw_input()
            buffer += "\n"

            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        client.close()


# 执行命令
def run_command(command):

    command = command.rstrip()

    # 创建子进程，并执行command命令操作，父进程会在该过程中等待子进程运行至结束，并返回子进程的执行结果
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "[*] Failed to execute command.\r\n"

    return output


# 处理服务端接收到的客户端请求
def client_handler(client_socket, addr):

    global upload
    global execute
    global command
    global upload_destination

    # 在服务端制定的路径上写入数据
    if len(upload_destination):

        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("[*] Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("[*] Failed to save file to $s\r\n" % upload_destination)


    # 在服务端执行客户端发来的命令
    if len(execute):

        output = run_command(execute)

        client_socket.send(output)


    # 在客户端与服务端建立起一个shell
    if command:

        while True:

            label = "<netcat-%s:%d>" %(addr[0], addr[1])
            client_socket.send(label)

            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                if str(cmd_buffer.rstrip()) == "quit":
                    sys.exit(0)


            response = run_command(cmd_buffer)

            client_socket.send(response)


# 开启制定的监听，并接受客户端的链接，并将链接请求服务加油多线程执行
def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        print "connect: %s:%d" %(addr[0], addr[1])

        client_threading = threading.Thread(target=client_handler, args=(client_socket, addr))

        client_threading.start()


def do_main():
    global listen
    global command
    global upload
    global execute
    global target
    global upload_destination
    global port

    #无输入参数，执行帮助
    if not len(sys.argv[1:]):
        usage()

    #读取命令行选项
    # getopt(args, shortopts, longopts = [])
    # shortopts 短格式，位于"-"后，如下的"hle:t:p:cu:"中，后无":"，代表不带参数，反之则带参数
    # longopts 长格式，位于"--"后，后有"="表示带参数，反之则表示不
    # opts返回值表示格式符与参数的元祖tuple列表,args则只有参数无格式符
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload", "test"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = True
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("--test"):
            print "it ok!"
        else:
            assert False, "Invalid argument!"

    # 无监听，说明是客户端，读取系统缓冲区，并发送到制定的服务端
    if not listen and len(target) and port > 0:

        buffer = sys.stdin.read()

        client_sender(buffer)


    # 监听状态，执行服务端代码
    if listen:
        server_loop()



if __name__ == '__main__':
    do_main()