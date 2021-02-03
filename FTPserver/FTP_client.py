import socket, sys, time

ADDR = ('127.0.0.1', 8888)


class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            data = self.sockfd.recv(1024)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('谢谢使用')

    def do_get(self, filename):
        self.sockfd.send(b'G ' + filename.encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            fd = open(filename, 'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        try:
            fd = open(filename, 'rb')
        except Exception:
            print("文件不存在！")
            return
        else:
            filename = filename.split('/')[-1]
            self.sockfd.send(b'P ' + filename.encode())
            data = self.sockfd.recv(1024).decode()
            if data == 'OK':
                while True:
                    data = fd.read(1024)
                    if not data:
                        time.sleep(0.1)
                        self.sockfd.send(b'##')
                        break
                    self.sockfd.send(data)
                fd.close()
                re = self.sockfd.recv(1024).decode()
                print(re)
            else:
                print(data)


# 发起请求
def request(s):
    ftp = FtpClient(s)
    while True:
        print("\n========请输入以下命令========")
        print("**********   list   **********")
        print("********** get file **********")
        print("********** put file **********")
        print("**********   quit   **********")
        print("==============================")
        cmd = input("输入命令：")
        if cmd.strip().lower() == "list":
            ftp.do_list()
        elif cmd.strip().lower() == 'quit':
            ftp.do_quit()
        elif cmd[:3].strip().lower() == 'get':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3].strip().lower() == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)


def main():
    s = socket.socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print("服务器连接失败！")
        return
    else:
        print(25*"*" + "\n" + "data     file     image\n" + 25*"*")
        cls = input("请输入文件种类：")
        if cls not in ['data', 'file', 'image']:
            print('没有您要找的文件！')
            return
        else:
            s.send(cls.encode())
            request(s)
    re = s.recv(1024)
    print(re.decode())
    s.close()


if __name__ == '__main__':
    main()