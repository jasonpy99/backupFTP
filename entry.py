# coding:utf8

import configparser
import os
import socket
import sys
import time
from ftplib import FTP


def read_config():
    """读取配置文件
    """
    a_config = configparser.ConfigParser()
    a_config.read('config.ini')
    return a_config


def confirm_configuration_completed(a_config):
    """
    确认配置文件里有必要的ftp配置文件信息
    :param a_config: 传入的配置文件实例
    :return: True: 包含必备的信息
    TODO: 添加格式的检验
    """
    nessary_items = ['address', 'name', 'password', 'port']
    return set(nessary_items).issubset(set(a_config['ftp']))


class BackupFTP:
    def __init__(self, a_config):
        self.file_list = []
        self.address = a_config['address']
        self.name = a_config['name']
        self.password = a_config['password']
        self.port = int(a_config['port'])
        self.ftp = FTP()
        self.remote_dir = a_config['remote_dir']

    def __del__(self):
        self.ftp.close()

    def login(self):
        ftp = self.ftp
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            print('connecting')
            ftp.connect(self.address, self.port)
            ftp.login(self.name, self.password)
            ftp.cwd(self.remote_dir)
            print(ftp.getwelcome())
        except Exception as e:
            print_error(e)

    def download_dir(self, localdir='./', remotedir='./'):
        try:
            self.ftp.cwd(remotedir)
        except Exception as e:
            print("No dir named %s and there's an error%s "% (remotedir, e) )
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remote_names = self.file_list
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(localdir, file_name)
            if file_type == 'd':
                self.download_files(local, file_name)
            elif file_type == '-':
                self.download_file(local, file_name)
        self.ftp.cwd('..')

    def get_file_list(self, line):
        """
        获取当前目录的所有文件名和目录名以及文件夹标志
        :param line:从dir函数获取的一行
        """
        file_infors = self.get_file_name(line)
        # 排除默认的. 和 .. 两个文件夹
        if file_infors[1] not in ['.', '..']:
            self.file_list.append(file_infors)

    def get_file_name(self, line):
        """
        从传入的一行数据里提取出文件名或者文件夹名
        传入数据格式： -rw-r--r--    1 0        0         3096506 Feb 12 01:02 access_20160211.log，第一个字符是文件类型，文件夹是d
        :param line: 传入的行
        :return: [文件夹标志，文件或者文件夹名]
        """
        # 保存文件夹标志
        file_arr = [line[0]]
        temp = line.split(' ')
        filter_infor = []
        for x in temp:
            if x != "":
                filter_infor.append(x)
        file_arr.append(filter_infor[8])
        return file_arr


def print_error(e):
    date_now = time.strftime('%Y %m %d', time.localtime())
    print("%s error occurred : %s" % (date_now, e))
    sys.exit()

if __name__ == '__main__':
    # 先获取配置文件
    config = read_config()
    if confirm_configuration_completed(config):
        aFtp = BackupFTP(config['ftp'])
        aFtp.login()

    else:
        print("The config file is not completed")
        # for key in config['ftp']:
        #     print(config['ftp'][str(key)])

config = read_config()
aFtp = BackupFTP(config['ftp'])
aFtp.login()
