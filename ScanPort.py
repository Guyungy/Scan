import os
from sys import argv
import telnetlib
import threading
import queue
import time


def get_ip_status(ip, port):
    server = telnetlib.Telnet()
    try:
        server.open(ip, port, 1)
        iplist.append(f'{ip}:{port}\n')
    except Exception as err:
        pass
    finally:
        server.close()


def check_open(q, p):
    try:
        while True:
            ip = q.get_nowait()
            get_ip_status(ip, p)
    except queue.Empty as e:
        pass


def ips(start, end):
    import socket
    import struct
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0]
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end+1) if i & 0xff]


def process_bar():
    while not q.empty():
        i = (qsize - q.qsize()) / qsize * 100
        print("\r扫描进度: {}{}  {:>5.1f}% | 100%".format(
            "▋" * (int(i) // 2), ' ' * ((101 - int(i)) // 2), i), end="", flush=True)
    print("\r扫描进度: {}  {:>5.1f}% | 100%".format(
        "▋" * 50, 100), end="", flush=True)


def helpstr():
    return f'''
                       欢迎使用 ScanPort v1.0
                              By:jflmao


  用法：
      {os.path.basename(__file__)} [-h]

      {os.path.basename(__file__)} [-i <0.0.0.0-255.255.255.255>] [-p <80>] [-t <500>]
    
  命令解释：
      -h       显示此帮助
      -i       IP地址范围
      -p       端口，可省略，默认65432
      -t       线程数，可省略，默认500线程

    '''


if __name__ == '__main__':
    # print(os.path.basename(__file__))  # 当前文件名名称
    start_time = time.time()  # 脚本开始执行的时间
    q = queue.Queue()
    port = 65432  # 需要扫描的端口号
    iplist = []  # 开放端口的IP列表
    #ipslist = ips('185.212.0.1', '185.212.255.255')  # 扫描的IP范围
    threadNum = 500  # 默认线程数

    if len(argv) > 1:
        if '-h' == argv[1]:
            print(helpstr())
            exit()
        for i, item in enumerate(argv):
            if '-i' in item:
                ip = argv[i+1].split('-')
                ipslist = ips(ip[0], ip[1])
            elif '-p' in item:
                port = int(argv[i+1])
            elif '-t' in item:
                threadNum = int(argv[i+1])
            else:
                pass
    else:
        print(helpstr())
        exit()

    for i in ipslist:
        q.put(i)
    qsize = q.qsize()  # 总任务数
    process = threading.Thread(target=process_bar)
    process.start()  # 创建进度条线程，并启动
    threads = []  # 线程列表
    for i in range(threadNum):
        t = threading.Thread(target=check_open, args=(q, port))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    process.join()

    with open('iplist.txt', 'a+') as f:  # 存入文件
        f.seek(0)
        list1 = f.readlines()  # 按行读取，返回列表
        list1.extend(iplist)  # 合并新列表
        list1 = list(set(list1))  # 去重
        list1.sort()  # 排序
        f.seek(0)  # 文件指针移到开头
        f.truncate()  # 清空
        f.writelines(list1)  # 写入

    print(f'\n本次扫描到开放[{port}]端口的IP数为 {len(iplist)} 个')
    end_time = time.time()  # 脚本结束执行的时间
    print("[脚本运行时间] %3ss" % (end_time-start_time,))
