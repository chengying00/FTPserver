"""FTP网络服务器，并发功能"""

import socket, threading, signal, sys, os, time

ADDR = ('0.0.0.0', 8888)
FTP = '/home/chengying/py_practice/FTP/'


# 将客户端功能封装为类
class FtpServer:
    def __init__(self, c, ftp_path):
        self.c = c
        self.path = ftp_path

    def do_list(self):
        # 获取路径下的所有文件，返回列表
        files = os.listdir(self.path)
        if not files:
            self.c.send("该文件类别为空.".encode())
            return
        else:
            self.c.send(b'OK')
            time.sleep(0.1)

        # 获取内容，一次性发送
        fs = ''
        for file in files:
            # 判断文件不是隐藏文件并且是普通文件
            if file[0] != '.' and os.path.isfile(self.path+file):
                fs += file + '\n'
        self.c.send(fs.encode())

    def do_get(self, filename):
        try:
            fd = open(self.path + filename, 'rb')
        except Exception:
            self.c.send('文件不存在！'.encode())
            return
        else:
            self.c.send(b'OK')
            time.sleep(0.1)
        while True:
            data = fd.read(1024)
            if not data:
                time.sleep(0.1)
                self.c.send(b'##')
                break
            self.c.send(data)

    def do_put(self, filename, path):
        if os.path.exists(self.path + filename):
            self.c.send('该文件已经存在！'.encode())
            return
        self.c.send(b'OK')
        fd = open(path + filename, 'wb')
        while True:
            data = self.c.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()
        self.c.send("文件上传成功！".encode())


def handle(c):
    while True:
        cls = c.recv(1024).decode()
        print(cls)
        FTP_PATH = FTP + cls + "/"
        ftp = FtpServer(c, FTP_PATH)
        while True:
            data = c.recv(1024).decode()
            if not data or data[0] == 'Q':
                return
            elif data[0] == 'L':
                print(data)
                ftp.do_list()
            elif data[0] == 'G':
                filename = data.split(' ')[-1]
                ftp.do_get(filename)
            elif data[0] == "P":
                filename = data.split(' ')[-1]
                ftp.do_put(filename, FTP_PATH)


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    s.listen(3)
    print("监听中......")

    while True:
        try:
            c, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("服务退出")
        except Exception as e:
            print(e)
            continue
        print("链接的客户端：", addr)
        t = threading.Thread(target=handle, args=(c,))
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    main()


