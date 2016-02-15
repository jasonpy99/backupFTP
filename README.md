# backupFTP
FTP的备份工具，python3写的。由于多备份停止了免费额度，只好自己写个工具来进行备份。在[linux下配合corn服务](http://www.findspace.name/res/902)可进行定时备份。
#使用环境
支持python3的环境
#配置文件
新建`config.ini`配置文件配置文件格式如下：
```ini
[ftp]
# ftp登录的地址
address = your_ftp_address
# 登录用户名
name = your_user_name
# 登录密码
password = your_password
# 登录端口，默认21
port = 21
# 需要下载的绝对路径
remote_dir = /wwwroot/adds/
# 需要下载到本地的路径，如果使用相对路径，请用./开头,如果是绝对路径，请以/开头。默认是./back/此项非必需,可直接去掉
local_dir = 
```
#运行
```bash
python3 entry.py
```
则自动将远程的目录下载到当前文件夹下
#TODO List
增加数据库备份功能
增加增量备份功能
增加备份到百度云等云端存储的功能
增加邮件通知功能