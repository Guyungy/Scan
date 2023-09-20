import threading
import queue
import sys
import time
import requests


def test_Sign_in(ip):
    requests.packages.urllib3.disable_warnings()
    sess = requests.Session()
    headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/plain, */*',
        'Origin': f'http://{ip}',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3904.108 Safari/537.36',
        'DNT': '1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': f'http://{ip}/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    data = {
        'username': 'admin',
        'password': 'admin'
    }
    try:
        sess.headers.update(headers)
        response = sess.post(f'http://{ip}/login', data=data, timeout=5, verify=False)
        res = response.json()['msg']
        if '登录成功' in res:
            okiplist.append(f'http://{ip}\n')
            print(f'[http://{ip}]{res}')
    except:
        #print("Unexpected error:", sys.exc_info()[0])
        pass


def check_open(q):
    try:
        while True:
            ip = q.get_nowait()
            test_Sign_in(ip)
    except queue.Empty as e:
        pass


if __name__ == '__main__':
    start_time = time.time()  # 脚本开始执行的时间
    okiplist = []
    q = queue.Queue()
    with open('iplist.txt', 'r+') as f:
        for ip in f.readlines():
            q.put(ip.strip())

    threads = []
    for i in range(10):#10个线程
        r = threading.Thread(target=check_open, args=(q,))
        r.start()
        threads.append(r)

    for t in threads:
        t.join()

    with open('okiplist.txt', 'a+') as f:
        f.seek(0)
        list1 = f.readlines()#按行读取，返回列表
        list1.extend(okiplist)#合并新列表
        list1 = list(set(list1))#去重
        list1.sort()  # 排序
        f.seek(0)  # 文件指针移到开头
        f.truncate()  # 清空
        f.writelines(list1)  # 写入
    end_time = time.time()  # 脚本结束执行的时间
    print("[脚本运行时间] %3ss" % (end_time-start_time,))
