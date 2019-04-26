# encoding: utf-8
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from imp import reload

import redis
from django.shortcuts import render
from django.http import HttpResponse
import sys
import json
from django.views.decorators.csrf import csrf_exempt
import hashlib

from api.models import Users

default_encoding = 'utf-8'

# Create your views here.

r = redis.StrictRedis(host='localhost', port='6379', db=0)

reload(sys)
@csrf_exempt
def register(request):
    '''注册用户'''
    #data = json.loads(request.body)
    data = request.POST.copy()
    try:
        # 判断是否已存在该邮箱注册的账号
        if not ('username' in data and 'password'in data):
            raise Exception('注册信息参数不完整')
        if Users().find_one_by_username(data['username']) is not None:
            raise Exception('用户已被注册过')
        # 插入数据
        # 将下面一行注释掉，取消MD5再次加密
        # data['password'] = MD5(data['password'])
        # 设初始labels为空，个性化推荐用
        #data['labels'] = {}

        map = {}
        map['username'] = data['username']
        map['password'] = data['password']
        map['labels'] = {}
        map['head'] = {}
        Users().insert_one(map)
        #print map['session']

        res = {
            'status': 0,
            'msg': '用户注册成功！',
            'result': True,
        }
    except Exception as e:
        res = {
            'status': 1,
            'msg': '用户注册失败！',
            'reason': str(e),
            'result': False,
        }

    # 已经生成了session，并且被加入到cookie中
    request.session['sessionId'] = data['username']
    print (request.session['sessionId'])

    res = json.dumps(res, indent=4, ensure_ascii=False)
    # response = HttpResponse(res, content_type='application/json')
    #
    # return response
    return HttpResponse(res, content_type='application/json')

@csrf_exempt
def login(request):
    '''用户登录'''
    #data = json.loads(request.body)
    data = request.POST.copy()
    try:
        if not ('username'in data and 'password' in data):
            raise Exception('账户或密码缺失')
        if Users().find_one_by_username(data['username']) is None:
            raise Exception('该账户并未注册')
        id = Users().find_one_by_username(data['username'])['_id']
        if check_password(id, data['password']) is False:
            raise Exception('密码不正确')

        # 获取数据
        user = Users().find_one(id=id)
        # 出于安全性，将password字段去掉
        del user['password']
        del user['_id']
        # 准备文章数据，转换为 JSON
        user['status'] = 0
        user['msg'] = str('用户登录成功！')
        user['result'] = True
        # if session_exist(user['username']) is False:
        #     request.session['sessionId'] = user['username']
        res = json.dumps(user, indent=4)
        return HttpResponse(res, content_type='application/json')
    except Exception as e:
        res = {
            'status': 1,
            'msg': '用户登录失败！',
            'reason': str(e),
            'result': False,
        }
    # if session_exist(data['username']) is False:
    #     request.session['sessionId'] = data['username']
    res = json.dumps(res, indent=4, ensure_ascii=False)
    return HttpResponse(res, content_type='application/json')

#如果没有session，就tm给我创建一个
def session_exist(userid):
    if r.exists('sessionId:%s' %userid):
        #以username为value的session存储存在
        return True
    return False

# 根据id，进行密码验证
def check_password(id, password):
    realPwd = Users().get_password_by_id(id)
    if password == realPwd:
        return True
    else:
        return False