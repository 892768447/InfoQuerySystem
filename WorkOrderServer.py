"""
Created on 2017年12月31日
@author: Irony
@site: https://github.com/892768447
@email: 892768447@qq.com
@file: WorkOrderServer
@description: 
"""
import atexit
import signal

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options

from WorkOrderApplication import WorkOrderApplication


__Author__ = 'By: Irony\nQQ: 892768447\nEmail: 892768447@qq.com'
__Copyright__ = 'Copyright (c) ${year} Irony'
__Version__ = 1.0

# from WorkOrderModel import initDb
define('debug', default=False, type=bool, help='调试模式')
define('maintenance', default=False, type=bool, help='是否在维护')
define('allow_days', default=15, type=int, help='显示多少天内的数据')
define('allow_upload_size', default=10, type=int, help='允许上传的最大文件大小(M)')
define('allow_upload_ext', type=list, help='允许上传的文件类型',
       default=['png', 'jpg', 'bmp', 'zip', 'rar', '7z', 'tar'])
define('file_format', type=str, help='保存文件名格式化样式',
       default='uploads/%Y/%m/%d/%Y.%m.%d-%H.%M.%S=={name}.{ext}')
define('server_ip', default='', type=str, help='服务器IP地址')
define('server_port', default=6666, type=int, help='服务器端口')
define('mysql_ip', default='127.0.0.1', type=str, help='MYSQL数据库IP地址')
define('mysql_port', default='3306', type=str, help='MYSQL数据库端口')
define('mysql_name', default='workorder', type=str, help='数据库')
define('mysql_user', default='root', type=str, help='MYSQL数据库用户名')
define('mysql_pwd', default='aj1@msmobile', type=str, help='MYSQL数据库密码')
# define('pool_pre_ping', default=True, type=bool, help='')
define('pool_recycle', default=3600, type=int, help='线程回收时间')
define('pool_size', default=5, type=int, help='线程池、连接池数量')


def start():
    options.parse_command_line()
    server = HTTPServer(WorkOrderApplication(), xheaders=True)
    server.listen(options.server_port, options.server_ip)
    print('Server Running On:{0}, Port:{1}'.format(
        options.server_ip, options.server_port))
    IOLoop.instance().start()


def stop():
    IOLoop.instance().stop()


if __name__ == '__main__':
    atexit.register(stop)
    signal.signal(signal.SIGTERM, stop)
    # 初始化数据库
#     initDb()
    # 运行服务器
    start()
