#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2018年1月3日
@author: Irony
@site: http://github.com/892768447
@email: 892768447@qq.com
@file: WorkOrderUtil
@description: 
"""


import base64
import json
import os
from random import randint
import traceback

from tornado.concurrent import run_on_executor
from tornado.ioloop import IOLoop
from tornado.options import options

import xxtea  # @UnresolvedImport


__Author__ = 'By: Irony\nQQ: 892768447\nEmail: 892768447@qq.com'
__Copyright__ = 'Copyright (c) ${year} Irony'
__Version__ = 1.0


class ResultCode(int):

    def __new__(self, code, value):
        obj = super(ResultCode, self).__new__(self, code)
        obj._value = value
        return obj

    @property
    def value(self):
        return self._value


class AsyncUtil:

    _threadpool = None  # type: ignore
    _threadpool_pid = None  # type: int

    def __init__(self, io_loop=None):
        self.executor = AsyncUtil._create_threadpool(options.pool_size)
        self.io_loop = io_loop or IOLoop.current()

    @run_on_executor
    def run(self, func, *args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            return ret
        except Exception as e:
            return str(e), None

    @classmethod
    def shutdown(cls):
        if cls._threadpool != None:
            cls._threadpool.shutdown()

    @classmethod
    def _create_threadpool(cls, num_threads):
        pid = os.getpid()
        if cls._threadpool_pid != pid:
            cls._threadpool = None
        if cls._threadpool is None:
            from concurrent.futures import ThreadPoolExecutor
            cls._threadpool = ThreadPoolExecutor(num_threads)
            cls._threadpool_pid = pid
        return cls._threadpool


def encrypt(data):
    """
    :param data: str or bytes
    """
    try:
        key = os.urandom(16)
        plen = randint(1, 9)
        padding = os.urandom(plen)
        # key + padding len + padding + data
        return key + hex(plen).encode() + padding + xxtea.encrypt(data, key)
    except:
        traceback.print_exc()
    return b''


def decrypt(data):
    """
    :param data: str or bytes
    """
    try:
        data = data.encode() if isinstance(data, str) else data
        key = data[:16]
        offset = 16 + 3 + int(data[16:19].decode(), 16)
        return xxtea.decrypt(data[offset:], key)
    except:
        traceback.print_exc()
    return b''


def encrypt_to_base64(data):
    """
    :param data: str or bytes
    """
    try:
        return base64.a85encode(encrypt(data))
    except:
        traceback.print_exc()
    return b''


def encrypt_to_base64_to_str(data):
    """
    :param data: str or bytes
    """
    if not data:
        return ''
    try:
        return encrypt_to_base64(data).decode()
    except:
        traceback.print_exc()
    return ''


def decrypt_to_str(data):
    """
    :param data: str or bytes
    """
    return decrypt(data).decode()


def decrypt_from_base64(data):
    """
    :param data: str or bytes
    """
    try:
        return decrypt(base64.a85decode(data.encode() if isinstance(data, str) else data))
    except:
        traceback.print_exc()
    return b''


def decrypt_from_base64_to_str(data):
    """
    :param data: str or bytes
    """
    if not data:
        return ''
    return decrypt_from_base64(data).decode()


class WorkOrderResult(dict):

    def __init__(self, code=200, msg='', data='', version=1.0):
        super(WorkOrderResult, self).__init__(
            code=code, msg=msg,
            data=encrypt_to_base64_to_str(json.dumps(data, separators=(
                ',', ':')) if isinstance(data, dict) or isinstance(data, list) else data),
            version=version
        )


if __name__ == '__main__':
    code = ResultCode(0, '错误')
    print(code, code.value)
    ##
    result = WorkOrderResult(data=b'def')
    print(result, decrypt_from_base64(result.get('data')))
    print(json.dumps(result))
    result = WorkOrderResult(data='abc')
    print(result, decrypt_from_base64_to_str(result.get('data')))
    print(json.dumps(result))
    data = 'test'
    print('**encrypt test**')
    a = encrypt(data)
    b = encrypt_to_base64(data)
    c = encrypt_to_base64_to_str(data)
    print('encrypt:', a)
    print('encrypt_to_base64:', b)
    print('encrypt_to_base64_to_str:', c)
    print('**decrypt test**')
    a = decrypt(a)
    b = decrypt_from_base64(b)
    c = decrypt_from_base64_to_str(c)
    print('decrypt:', a)
    print('decrypt_from_base64:', b)
    print('decrypt_from_base64_to_str:', c)
