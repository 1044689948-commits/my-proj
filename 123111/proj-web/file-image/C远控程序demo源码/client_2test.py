import socket
import threading
import os

#解析收到的命令
def recv_client_msg(client_sock):
    while True:
        # recv 返回值是字节串-记得解码

        cmd =client_sock.recv(1024).decode()
        cmd =cmd.split(" ")  #分割
        #如果结果为空，说明对方断开了连接
        if not cmd :
            break
        #如果是执行上传文件命令

        if cmd[0] == 'upload_file':
            recv_upload(client_sock,cmd)
        elif cmd[0] == "os-shell":
            os_shell(client_sock)
        elif cmd[0] == 'image':
            send_photo(client_sock,cmd)
        elif cmd[0] == 'download_file':
            recv_download(client_sock,cmd)

        print(cmd[0])

def recv_upload(client_sock,cmd):
    pass
def os_shell(client_sock):
    pass
def  send_photo(client_sock,cmd):
    pass
def recv_download(client_sock,cmd):
    pass

#创建套接字
sock = socket.socket()
client_sock = sock
#等待连接
sock.connect(('127.0.0.1',12335))
#创建线程发送来的消息
t= threading.Thread(target=recv_client_msg,args=(sock,))
t.start()
#给服务器发消息
while True:
    data = input('请输入要发送的内容>>>')
    if data == 'exit':
        break
    sock.send(data.encode())
#关闭套接字
sock.close()


