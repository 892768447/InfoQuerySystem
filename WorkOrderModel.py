#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2017年12月27日
@author: Irony
@site: http://github.com/892768447
@email: 892768447@qq.com
@file: WorkOrderModel
@description: 
"""
from datetime import datetime
import json

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import text, and_, or_
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, CHAR, VARCHAR, TIMESTAMP, TEXT, DATETIME
from tornado.log import gen_log
from tornado.options import options

from WorkOrderUtil import ResultCode


__Author__ = 'By: Irony\nQQ: 892768447\nEmail: 892768447@qq.com'
__Copyright__ = 'Copyright (c) ${year} Irony'
__Version__ = 1.0

Base = declarative_base()
SESSION = None


class BaseModel:

    def __repr__(self):
        return '\n<%s(\n\t' % self.__tablename__ + '\n\t'.join(
            ['{0}={1}'.format(key, value) for key, value in self.to_dict(True).items()]) + '\n)>'

    def to_dict(self, datetostr=False)->dict:
        """类对象转dict
        :return: ``dict``
        """
        _dict = self.__dict__.copy()  # 不能在原有上面修改
        _dict.pop('_sa_instance_state', None)
        for key in list(_dict.keys()):
            if isinstance(_dict.get(key), datetime) and datetostr:  # 转换时间
                _dict[key] = _dict.get(key).strftime('%Y-%m-%d %H:%M:%S')
        return _dict

    def to_json(self)->str:
        """类对象转json
        :return: ``str``
        """
        return json.dumps(self.to_dict(True))

    @classmethod
    def toDicts(cls, items)->list:
        """所有查询结果中的类对象转dict"""
        return [item.to_dict() for item in items]

    @classmethod
    def toJsons(cls, items)->list:
        """所有查询结果中的类对象转json
        :param items: 查询的结果列表
        :return: ``list``
        """
        return [item.to_json() for item in items]

    @classmethod
    def _insert(cls, entity: object)->int:
        '''插入封装
        :param cls:
        :param entity: :class:`BaseModel`
        '''
        if not SESSION:
            gen_log.error('session is null')
            return ResultCode(0, '无法获取session对象,数据库可能连接错误')
        session = SESSION()
        try:
            session.add(entity)
            session.commit()
            session.close()
            gen_log.debug('add {entity} successed'.format(entity=entity))
            return ResultCode(1, '插入成功')
        except Exception as e:
            gen_log.warning(
                'add {entity} failed, error: {e}'.format(entity=entity, e=e))
        session.close()
        return ResultCode(0, '插入失败')

    @classmethod
    def query(cls, field: str, value: object)->(None, list):
        """根据指定字段查询
        :param cls:
        :param field: 字段
        :param value: 值
        :return: ``None`` 或者 ``list``
        """
        if not SESSION:
            gen_log.error('session is null')
            return None
        session = SESSION()
        try:
            ret = session.query(cls).filter(field == value).all()
            session.close()
            return ret
        except Exception as e:
            gen_log.warning(
                'query {model}({field}={value}) failed, error: {e}'.format(
                    model=cls, field=field, value=value, e=e))
        session.close()
        return None

    @classmethod
    def delete(cls, field: str, value: object)->int:
        '''根据指定字段和值删除
        :param cls:
        :param field: 字段
        :param value: 值
        :return: ``int``
        '''
        if not SESSION:
            gen_log.error('session is null')
            return ResultCode(0, '无法获取session对象,数据库可能连接错误')
        session = SESSION()
        try:
            ret = session.query(cls).filter(field == value).delete()
            session.commit()
            session.close()
            return ret
        except Exception as e:
            gen_log.warning(
                'delete {model}({field}={value}) failed, error: {e}'.format(
                    model=cls, field=field, value=value, e=e))
        session.close()
        return ResultCode(0, '删除失败')

    @classmethod
    def get_all(cls, limit: int=0, order_by_field: Column=None, desc: bool=True)->list:
        '''查询所有结果
        :param cls:
        :param limit: 限制数量
        :param order_by_field: 排序字段
        :param desc: 默认倒序
        :return: ``list``
        '''
        if not SESSION:
            gen_log.error('session is null')
            return []
        session = SESSION()
        try:
            query = session.query(cls)
            if limit:
                query = query.limit(limit)
            if order_by_field:
                query = query.order_by(
                    order_by_field.desc() if desc else order_by_field)
            result = query.all() or []
            session.close()
            return result
        except Exception as e:
            gen_log.warning(
                'get all {model}(limit={limit}, order_by_field={order_by_field}, '
                'desc={desc}) failed, error: {3}'.format(
                    model=cls, limit=limit, order_by_field=order_by_field, desc=desc, e=e))
        session.close()
        return []

    @classmethod
    def _get_all(cls, method: str, limit: int=0, order_by_field: Column=None)->list:
        '''获取所有结果并根据提供的method来决定是转换为json还是dict
        :param cls:
        :param method: to_dict 或者 to_json
        :param limit: 限制数量
        :param order_by_field: 排序字段
        :return: ``list``
        '''
        items = cls.get_all(limit, order_by_field)
        if not items:
            return items
        if str(type(items[0])).find('_collections.result') == -1:
            return [getattr(item, method)() for item in items]
        # 需要转换
        _items = []
        for item in items:
            keys = item.keys()
            models = [getattr(item, model) for model in keys if isinstance(
                getattr(item, model), BaseModel)]
            others = [other for other in keys if not isinstance(
                getattr(item, other), BaseModel)]
            model = models[0]
            for m in models[1:]:
                model += m
            for o in others:
                model += (o, getattr(item, o))
            _items.append(model)
        return [getattr(item, method)() for item in _items]

    @classmethod
    def get_all_dict(cls, limit: int=0, order_by_field: Column=None)->list:
        '''获取所有结果并转换为dict类型
        :param cls:
        :param limit: 限制数量
        :param order_by_field: 排序字段
        :return: ``list``
        '''
        return cls._get_all("to_dict", limit, order_by_field)

    @classmethod
    def get_all_json(cls, limit: int=0, order_by_field: Column=None)->list:
        '''获取所有结果并转换为json
        :param cls:
        :param limit: 限制数量
        :param order_by_field: 排序字段
        :return: ``list``
        '''
        return cls._get_all("to_json", limit, order_by_field)

    def __add__(self, other):
        '''model相加
        :param other: ``tuple'' 或者 :class:`BaseModel`
        :return: :class:`BaseModel`
        '''
        if isinstance(other, BaseModel):
            for key, value in other.to_dict().items():
                if not key in self.__dict__:
                    self.__dict__[key] = value
                else:
                    self.__dict__[other.__tablename__ + '_' + key] = value
        elif isinstance(other, tuple):
            self.__dict__[other[0]] = str(other[1])
        return self


class GroupsModel(BaseModel, Base):
    """分组表"""
    __tablename__ = 'groups'
    group_id = Column(BigInteger, primary_key=True,
                      autoincrement=True, doc='分组ID')
    group_name = Column(VARCHAR(255), unique=True, doc='分组名称')

    @classmethod
    def insert(cls, group_name: str)->int:
        '''插入分组
        :param cls:
        :param group_name: 分组名
        :return: ``int`` 0(fail) 1(success)
        '''
        return cls._insert(cls(group_name=group_name))


class LogsModel(BaseModel, Base):
    """日志表"""
    __tablename__ = 'logs'
    log_id = Column(BigInteger, primary_key=True,
                    autoincrement=True, doc='索引id')
    user_id = Column(BigInteger, doc='用户ID')
    log_func = Column(VARCHAR(255), doc='操作名称')
    log_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), doc='操作时间')

    @classmethod
    def insert(cls, user_id: int, log_func: str)->int:
        '''插入操作日志
        :param cls:
        :param user_id: 用户的ID
        :param log_func: 操作名称
        :return: ``int`` 0(fail) 1(success)
        '''
        return cls._insert(cls(user_id=user_id, log_func=log_func))


class BugsModel(BaseModel, Base):
    """bug反馈表"""
    __tablename__ = 'bugs'
    bug_id = Column(BigInteger, primary_key=True,
                    autoincrement=True, doc='索引id')
    user_id = Column(Integer, doc='用户ID')
    bug_message = Column(TEXT, doc='错误日志')
    bug_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), doc='提交时间')

    @classmethod
    def insert(cls, user_id: int, bug_message: str)->int:
        '''插入bug反馈日志
        :param cls:
        :param user_id: 用户的ID
        :param bug_message: 错误日志
        :return: ``int`` 0(fail) 1(success)
        '''
        return cls._insert(cls(user_id=user_id, bug_message=bug_message))


class FeedsModel(BaseModel, Base):
    """反馈表"""
    __tablename__ = 'feeds'
    feed_id = Column(BigInteger, primary_key=True,
                     autoincrement=True, doc='索引id')
    user_id = Column(Integer, doc='用户ID')
    feed_message = Column(TEXT, doc='反馈消息')
    feed_read = Column(Integer, server_default=text('0'), doc='是否已读(0)')
    feed_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), doc='留言时间')

    @classmethod
    def insert(cls, user_id: int, feed_message: str)->int:
        '''插入反馈消息
        :param cls:
        :param user_id: 用户的ID
        :param feed_message: 反馈消息
        :return: ``int`` 0(fail) 1(success)
        '''
        return cls._insert(cls(user_id=user_id, feed_message=feed_message))


class FilesModel(BaseModel, Base):
    """附件表"""
    __tablename__ = 'files'
    file_md5 = Column(CHAR(32), primary_key=True,
                      autoincrement=False, doc='文件md5')
    form_code = Column(CHAR(32), nullable=False, index=True, doc='工单唯一编码')
    user_id = Column(Integer, nullable=False, doc='用户id')
    file_type = Column(VARCHAR(10), doc='文件类型(后缀)')
    file_name = Column(VARCHAR(255), doc='原始文件名')
    file_path = Column(VARCHAR(255), nullable=False, doc='文件储存路径')
    upload_time = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), doc='储存时间')

    @classmethod
    def insert(cls, file_md5: str, form_code: str, user_id: int,
               file_type: str, file_name: str, file_path: str):
        '''插入文件储信息
        :param cls:
        :param file_md5: 文件md5
        :param form_code: 工单唯一编码
        :param user_id: 用户id
        :param file_type: 文件类型(后缀)
        :param file_name: 原始文件名
        :param file_path: 文件储存路径
        '''
        return cls._insert(
            cls(
                file_md5=file_md5, form_code=form_code, user_id=user_id,
                file_type=file_type, file_name=file_name, file_path=file_path
            )
        )


class UsersModel(BaseModel, Base):
    """用户表"""
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True,
                     autoincrement=True, doc='索引id')
    group_id = Column(Integer, nullable=False,  doc='区县ID')
    user_state = Column(Integer, server_default=text('1'),
                        doc='帐号是否可用(1可用,0加锁)')
    user_mark = Column(TEXT, doc='备注')
    user_role = Column(VARCHAR(15), server_default=text('"普通用户"'), doc='用户角色')
    user_name = Column(VARCHAR(255), unique=True, doc='用户名')
    user_nick = Column(VARCHAR(255), doc='昵称')
    user_upwd = Column(CHAR(32), doc='3次md5加密后的密码')
    user_dpwd = Column(CHAR(32), doc='3次md5加密后的初始密码')
    user_ips = Column(VARCHAR(15), doc='用户运行的IP地址头比如192.168.1.')
    valid_time = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP'), doc='密码有效初始时间')

    @classmethod
    def login(cls, user_name, user_upwd, user_ip):
        """
        #用户登录
        :param cls:
        :param user_name: 帐号
        :param user_upwd: 密码
        :param user_ip: ip
        """
        if not SESSION:
            gen_log.error('session is null')
            return None
        err_msg = ''
        session = SESSION()
        try:
            user = session.query(cls).filter(user_name=user_name).first()
            session.close()
            if not user:
                return 0, '登录失败：用户不存在', None
            if user.user_dpwd == user_upwd:
                return 0, '不能使用默认密码登录，请先修改密码', None
            if user.user_upwd != user_upwd:
                return 0, '密码不正确', None
            if not user.user_state:
                return 0, '该帐号已被加锁：{0}'.format(user.user_mark), None
            if (datetime.now() - user.valid_time).days > 30:
                return 0, '密码已到期，请修改密码', None
            # 校验用户ip是否在运行的ip段内
            ip_valid = False
            for ip in user.user_ips.split(';'):
                if user_ip.startswith(ip):
                    ip_valid = True
                    break
            if not ip_valid:
                return 0, '该帐号不允许在该设备上登录，请联系管理员', None
            return 200, '登录成功', user.to_dict()
        except Exception as e:
            err_msg = str(e)
            gen_log.error(str(e))
        session.close()
        return 0, '登录失败： {0}'.format(err_msg), None

    @classmethod
    def register(cls, group_id, user_role, user_name,
                 user_nick, user_upwd, user_dpwd, user_ips):
        """
        #新增用户
        :param cls:
        :param group_id: 分组ID
        :param user_role: 角色
        :param user_name: 帐号
        :param user_nick: 昵称
        :param user_upwd: 密码
        :param user_dpwd: 默认密码
        :param user_ips: 允许IP范围
        """
        return cls._insert(cls(
            group_id=group_id, user_role=user_role,
            user_name=user_name, user_nick=user_nick,
            user_upwd=user_upwd, user_dpwd=user_dpwd, user_ips=user_ips))

    @classmethod
    def password(cls, user_name, user_upwd, user_npwd, reset=0):
        """
        #修改密码
        :param user_name: 帐号
        :param user_upwd: 原密码
        :param user_npwd: 新密码
        :param reset: 是否重置密码
        """
        if not SESSION:
            return 0, '数据库连接错误，请联系后台管理员', None
        err_msg = ''
        session = SESSION()
        try:
            if reset:  # 重置密码
                ret = session.query(cls).filter(user_name=user_name).update({
                    cls.user_upwd: user_npwd, cls.user_dpwd: user_npwd
                }, synchronize_session=False)
            else:  # 修改密码
                ret = session.query(cls).filter(
                    and_(cls.user_name == user_name,
                         or_(cls.user_upwd == user_upwd, cls.user_dpwd == user_upwd))).update({
                             cls.user_upwd: user_npwd, cls.user_dpwd: user_npwd
                         }, synchronize_session=False)
            session.commit()
            session.close()
            gen_log.debug('ret: {0}'.format(ret))
            return 200, '密码修改成功，请牢记，如果忘记请联系系统管理员', ret
        except Exception as e:
            err_msg = str(e)
            gen_log.error(str(e))
        session.close()
        return 0, '密码修改失败： {0}'.format(err_msg), None

    @classmethod
    def lock(cls, user_name, user_state):
        """
        #加解锁
        :param cls:
        :param user_name: 帐号
        :param user_state: 1-解锁,0-加锁
        """
        if not SESSION:
            return '数据库连接错误，请联系后台管理员', None
        err_msg = ''
        session = SESSION()
        try:
            # 更新状态
            ret = session.query(cls).filter(user_name=user_name).update(
                {cls.user_state: user_state}, synchronize_session=False)
            session.commit()
            session.close()
            gen_log.debug('ret: {0}'.format(ret))
            return '加解锁成功', ret
        except Exception as e:
            err_msg = str(e)
            gen_log.error(str(e))
        session.close()
        return '加解锁失败： {0}'.format(err_msg), None


class FormsModel(BaseModel, Base):
    """工单表"""
    __tablename__ = 'forms'
    form_id = Column(BigInteger, primary_key=True,
                     autoincrement=True, doc='索引id')
    form_number = Column(VARCHAR(255), doc='介绍信编号')
    form_code = Column(CHAR(32), doc='工单唯一编码ID')
    user_id = Column(Integer, doc='用户id')
    group_id = Column(Integer, doc='区县ID')
    form_urgent = Column(Integer, doc='紧急1或普通0')
    form_state = Column(CHAR(3), doc='工单状态(审批中)')
    form_detail = Column(TEXT, doc='工单说明')
    form_phones = Column(TEXT, doc='查询的手机号码')
    form_result = Column(TEXT, doc='处理结果')
    form_time = Column(DATETIME, doc='工单时间')


def initDb():
    engine = create_engine(
        'mysql+pymysql://root:aj1@msmobile@127.0.0.1/test',
        encoding='utf-8', echo=options.debug,
        #         pool_pre_ping=options.pool_pre_ping,
        pool_size=options.pool_size,
        pool_recycle=options.pool_recycle)
    Base.metadata.create_all(engine)
    global SESSION
    SESSION = sessionmaker(bind=engine)
