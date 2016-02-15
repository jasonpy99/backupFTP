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
    necessary_items = ['address', 'name', 'password', 'port']
    return set(necessary_items).issubset(set(a_config['ftp']))


class BackupFTP:
    def __init__(self, a_config):
        self.file_list = []
        self.address = a_config['address']
        self.name = a_config['name']
        self.password = a_config['password']
        self.port = int(a_config['port'])
        self.ftp = FTP()

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
            print(ftp.getwelcome())
        except Exception as e:
            print_error(e)

    def download_file(self, local_file, a_remote_file):
        print('download file %s' % local_file)
        file_handler = open(local_file, 'wb')
        self.ftp.retrbinary('RETR %s' % a_remote_file, file_handler.write)
        file_handler.close()

    def download_dir(self, a_local_dir='./', a_remote_dir='./'):
        """
        下载文件夹，
        :param a_local_dir:
        :param a_remote_dir:
        :return:
        """
        try:
            self.ftp.cwd(a_remote_dir)
        except Exception as e:
            print_error(e, "No dir named" + a_remote_dir)
        if not os.path.isdir(a_local_dir):
            os.makedirs(a_local_dir)
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remote_names = self.file_list
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(a_local_dir, file_name)
            if file_type == 'd':
                self.download_dir(local, file_name)
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

    @staticmethod
    def get_file_name(line):
        """
        从传入的一行数据里提取出文件名或者文件夹名
        传入数据格式： -rw-r--r--    1 0        0         3096506 Feb 12 01:02 access_20160211.log，第一个字符是文件类型，文件夹是d
        :param line: 传入的行
        :return: [文件夹标志，文件或者文件夹名]
        """
        # 保存文件夹标志
        file_arr = [line[0]]
        import re
        pattern = re.compile('[drwx-]{10}\s+?\d{1,2}\s+?\w+?\s+?\w+?\s+?\d+?\s+?[\d\w\u4e00-\u9fa5]+?\s+?\d+?\s+?[\d:]+?\s+?(.*)')
        match = pattern.match(line)
        if match:
            file_arr.append(match.group(1))
        else:
            print_error(err_str="match filename")
        return file_arr


def print_error(e='', err_str=''):
    """
    打印错误，并结束程序
    :param e: Exception 对象
    :param err_str: 自定义的错误输出
    :todo 这个函数的地方还有些别扭，需要改动
    """
    date_now_t = time.strftime('%Y %m %d', time.localtime())
    print("%s error occurred : %s \n%s" % (date_now_t, err_str, e))
    sys.exit()

if __name__ == '__main__':
    # 先获取配置文件
    config = read_config()
    if confirm_configuration_completed(config):
        aFtp = BackupFTP(config['ftp'])
        aFtp.login()
        config = read_config()
        aFtp = BackupFTP(config['ftp'])
        aFtp.login()
        if 'local_dir' in config['ftp'] and config['ftp']['local_dir'] != '':
            local_dir = os.path.join('./', config['ftp']['local_dir']+"/")
        else:
            local_dir = '.' + os.sep + 'back/'
        print(local_dir)
        remote_dir = config['ftp']['remote_dir']
        aFtp.download_dir(local_dir, remote_dir)
        time_now = time.localtime()
        date_now = time.strftime('%Y-%m-%d', time_now)
        print(" - %s successfully backed up\n" % date_now)
    else:
        print_error(err_str="The config file is not completed")

