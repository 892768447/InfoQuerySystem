"""
Created on 2017年12月31日
@author: Irony
@site: https://github.com/892768447
@email: 892768447@qq.com
@file: WorkOrderHandler
@description: 
"""
import functools
import json

from tornado.gen import coroutine
from tornado.options import options
from tornado.web import RequestHandler, asynchronous

from WorkOrderModel import FilesModel, UsersModel, GroupsModel, FeedsModel,\
    BugsModel
from WorkOrderUtil import WorkOrderResult, AsyncUtil


__Author__ = 'By: Irony\nQQ: 892768447\nEmail: 892768447@qq.com'
__Copyright__ = 'Copyright (c) ${year} Irony'
__Version__ = 1.0


def is_maintain(method):
    """判断服务器是否在维护"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if options.maintenance:    # 服务器正在维护
            return self.finish(WorkOrderResult(msg='服务器正在维护'))
        return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(RequestHandler):

    def get_current_user(self):
        """获取当前用户"""
        return self.get_secure_cookie('user')

    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header('Server', 'WorkOrder Server By:Irony QQ:892768447')

    def set_secure_cookie(self, name, value, expires_days=30, version=None, **
                          kwargs):
        if isinstance(value, dict):
            value = json.dumps(value, separators=(',', ':'))
        super(BaseHandler, self).set_secure_cookie(
            name, value, expires_days=expires_days, version=version, **kwargs)


class IndexHandler(BaseHandler):
    # 首页

    def get(self, *args, **kwargs):
        self.finish('ok')


class NoticeHandler(BaseHandler):
    # 公告

    def get(self, *args, **kwargs):
        self.finish(WorkOrderResult(msg=self.application.announcement))

    def post(self, *args, **kwargs):
        announcement = self.get_argument('announcement', None)
        if announcement == None:
            return self.finish(WorkOrderResult(0, '公告内容不能为空'))
        self.application.announcement = announcement
        self.finish(WorkOrderResult(msg='设置成功'))


class UrgentHandler(BaseHandler):
    # 紧急流程控制

    def get(self, *args, **kwargs):
        self.finish(WorkOrderResult(
            msg='ok', data=list(self.application.urgents)))

    def post(self, *args, **kwargs):
        user_id = self.get_argument('user_id', None)
        opt_type = self.get_argument('opt_type', None)
        if not user_id:
            return self.finish(WorkOrderResult(0, '参数有误'))
        if opt_type == '1':
            self.application.urgents.add(user_id)
            return self.finish(WorkOrderResult(msg='添加成功'))
        elif user_id in self.application.urgents:
            self.application.urgents.remove(user_id)
            return self.finish(WorkOrderResult(msg='删除成功'))
        self.finish(WorkOrderResult(msg='没有任何操作'))


class UserLoginHandler(BaseHandler):
    # 登录

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        # 获取表单中的帐号
        user_name = self.get_argument('user_name', None)
        if not user_name:
            return self.finish(WorkOrderResult(0, '帐号不能为空'))
        # 获取表单中的密码
        user_upwd = self.get_argument('user_upwd', None)
        if not user_upwd:
            return self.finish(WorkOrderResult(0, '密码不能为空'))
        # 获取访问者的IP地址
        user_ip = self.request.remote_ip
        # 后台线程异步请求
        code, msg, data = yield AsyncUtil().run(UsersModel.login, user_name, user_upwd, user_ip)
        if data:  # 设置私密cookie
            self.set_secure_cookie('user', data)
        self.finish(WorkOrderResult(code, msg, data))


class UserLogoutHandler(BaseHandler):
    # 注销

    def get(self, *args, **kwargs):
        self.clear_cookie('user')


class UserRegisterHandler(BaseHandler):
    # 新增用户

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        # 获取表单中的用户分组ID
        group_id = self.get_argument('group_id', None)
        if not group_id:
            return self.finish(WorkOrderResult(msg='用户分组不能为空'))
        # 获取表单中的用户角色
        user_role = self.get_argument('user_role', None)
        if not user_role:
            return self.finish(WorkOrderResult(msg='用户角色不能为空'))
        # 获取表单中的帐号
        user_name = self.get_argument('user_name', None)
        if not user_name:
            return self.finish(WorkOrderResult(msg='账号不能为空'))
        # 获取表单中用户的昵称
        user_nick = self.get_argument('user_nick', None)
        if not user_nick:
            return self.finish(WorkOrderResult(msg='昵称不能为空'))
        # 获取表单中的密码
        user_upwd = self.get_argument('user_upwd', None)
        if not user_upwd:
            return self.finish(WorkOrderResult(msg='密码不能为空'))
        # 获取表单中的默认密码
        user_dpwd = self.get_argument('user_dpwd', 'zzz123456')
        # 获取表单中允许用户的IP地址
        user_ips = self.get_argument('user_ips', None)
        if not user_ips:
            return self.finish(WorkOrderResult(msg='IP范围不能为空'))
        # 后台线程异步请求
        code, msg, _ = yield AsyncUtil().run(
            UsersModel.register, group_id, user_role, user_name,
            user_nick, user_upwd, user_dpwd, user_ips)
        self.finish(WorkOrderResult(code, msg))


class UserPasswordHandler(BaseHandler):
    # 密码修改

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        # 获取表单中的帐号
        user_name = self.get_argument('user_name', None)
        if not user_name:
            return self.finish(WorkOrderResult(msg='账号不能为空'))
        # 获取表单中的密码
        user_upwd = self.get_argument('user_upwd', None)
        if not user_upwd:
            return self.finish(WorkOrderResult(msg='密码不能为空'))
        # 获取表单中的新密码
        user_npwd = self.get_argument('user_npwd', None)
        if not user_npwd:
            return self.finish(WorkOrderResult(msg='新密码不能为空'))
        # 后台线程异步请求
        code, msg, _ = yield AsyncUtil().run(
            UsersModel.password, user_name, user_upwd, user_npwd)
        self.finish(WorkOrderResult(code, msg))


class UserStateHandler(BaseHandler):
    # 加解锁

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        # 获取表单中的帐号
        user_name = self.get_argument('user_name', None)
        if not user_name:
            return self.finish(WorkOrderResult(msg='账号不能为空'))
        # 获取表单中的操作
        user_state = self.get_argument('user_state', None)
        if not user_state:
            return self.finish(WorkOrderResult(msg='操作类型不能为空'))
        # 后台线程异步请求
        msg, _ = yield AsyncUtil().run(UsersModel.lock, user_name, user_state)
        self.finish(WorkOrderResult(msg=msg))


class UserListHandler(BaseHandler):
    # 用户列表

    @asynchronous
    @coroutine
    def get(self, *args, **kwargs):
        # 后台线程异步请求
        msg, data = yield AsyncUtil().run(UsersModel.get_all_dict)
        self.finish(WorkOrderResult(msg=msg, data=data))


class GroupAddHandler(BaseHandler):
    # 新增分组

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        group_name = self.get_argument('group_name', None)
        # 后台线程异步请求
        msg, _ = yield AsyncUtil().run(GroupsModel.insert, group_name)
        self.finish(WorkOrderResult(msg=msg))


class GroupListHandler(BaseHandler):
    # 分组列表

    @asynchronous
    @coroutine
    def get(self, *args, **kwargs):
        # 后台线程异步请求
        msg, data = yield AsyncUtil().run(GroupsModel.get_all_dict)
        self.finish(WorkOrderResult(msg=msg, data=data))


class FormListHandler(BaseHandler):
    # 获取工单

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FormAddHandler(BaseHandler):
    # 新增工单

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FormUpdateHandler(BaseHandler):
    # 工单更新

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FormQueryHandler(BaseHandler):
    # 工单查询

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FormExportHandler(BaseHandler):
    # 工单导出

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FeedAddHandler(BaseHandler):
    # 新增反馈

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class FeedListHandler(BaseHandler):
    # 获取反馈

    @asynchronous
    @coroutine
    def get(self, *args, **kwargs):
        # 后台线程异步请求
        msg, data = yield AsyncUtil().run(
            FeedsModel.get_all_dict, 200, FeedsModel.feed_time)
        self.finish(WorkOrderResult(msg=msg, data=data))


class FeedUpdateHandler(BaseHandler):
    # 反馈更新

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class BugAddHandler(BaseHandler):
    # 新增bug

    def post(self, *args, **kwargs):
        BaseHandler.post(self, *args, **kwargs)


class BugListHandler(BaseHandler):
    # 获取bug

    @asynchronous
    @coroutine
    def get(self, *args, **kwargs):
        # 后台线程异步请求
        msg, data = yield AsyncUtil().run(
            BugsModel.get_all_dict, 200, BugsModel.bug_time)
        self.finish(WorkOrderResult(msg=msg, data=data))


class FileUploadHandler(BaseHandler):
    # 文件上传

    @asynchronous
    @coroutine
    def post(self, *args, **kwargs):
        md5value = self.get_argument('md5value', None)  # 文件md5
        filename = self.get_argument('filename', None)  # 文件名
        filepath = self.get_argument('filepath', None)  # 文件路径
        formcode = self.get_argument('formcode', None)  # 工单编号
        if not filename or not filepath or not md5value:
            self.set_status(404)
            return self.finish(WorkOrderResult(code=404, msg='字段错误'))
        print(filename, filepath, md5value)
        if not FilesModel.insert(md5value, filename, filepath):
            self.set_status(404)
            return self.finish(WorkOrderResult(code=404, msg='文件已存在或保存错误'))
        self.finish(WorkOrderResult(msg='保存成功'))


Handlers = [
    (r'/user/login', UserLoginHandler),
    (r'/user/logout', UserLogoutHandler),
    (r'/user/register', UserRegisterHandler),
    (r'/user/password', UserPasswordHandler),
    (r'/user/valid', UserStateHandler),
    (r'/user/list', UserListHandler),
    (r'/group/add', GroupAddHandler),
    (r'/group/list', GroupListHandler),
    (r'/form/add', FormAddHandler),
    (r'/form/update', FormUpdateHandler),
    (r'/form/query', FormQueryHandler),
    (r'/form/export', FormExportHandler),
    (r'/form/list', FormListHandler),
    (r'/feed/add', FeedAddHandler),
    (r'/feed/list', FeedListHandler),
    (r'/feed/update', FeedUpdateHandler),
    (r'/bug/add', BugAddHandler),
    (r'/bug/list', BugListHandler),
    (r'/file/upload', FileUploadHandler),
    (r'/notice', NoticeHandler),
    (r'/urgent', UrgentHandler),
    (r'/.*?', IndexHandler)
]
