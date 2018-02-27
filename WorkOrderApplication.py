"""
Created on 2017年12月31日
@author: Irony
@site: https://github.com/892768447
@email: 892768447@qq.com
@file: WorkOrderApplication
@description: 
"""
import base64
import uuid

from tornado.web import Application

from WorkOrderHandler import Handlers


__Author__ = 'By: Irony\nQQ: 892768447\nEmail: 892768447@qq.com'
__Copyright__ = 'Copyright (c) ${year} Irony'
__Version__ = 1.0

class WorkOrderApplication(Application):
    
    announcement = ''  # 公告
    urgents = set()  # 允许紧急流程的用户

    @property
    def cookie_secret(self):
        return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

    def __init__(self):
        settings = {
            'cookie_secret': self.cookie_secret,
            'gzip': True
        }
        Application.__init__(self, Handlers, **settings)
