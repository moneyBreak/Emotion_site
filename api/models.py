#coding=utf8
import pymongo
from bson import ObjectId
from django.db import models
from django.conf import settings
# Create your models here.
from Emotion_site import settings


class Users:
    def __init__(self):
        '''初始化'''
        # 连接 mongo 数据库，获得数据指定集合
        self.client = pymongo.MongoClient('mongodb://%s:%s@%s:%d/%s' % (settings.
        MONGO_USER, settings.MONGO_PWD,
        settings.MONGO_HOST, settings.MONGO_PORT,
        settings.
        MONGO_AUTHDB))[settings.MONGO_DBNAME]
        self.users = self.client['users']

    def find_one(self, id):
        '''获取指定数据'''
        user = self.users.find_one({"_id": ObjectId(id)})
        return user

    def find_label(self, id):
        '''获取用户对应的labels'''
        user = self.users.find_one({"_id": ObjectId(id)})
        if user.has_key('labels'):
            return user['labels']
        else:  # 用户没有label
            return None

    def find_all(self):
        '''返回全部用户数据'''
        user_list = self.users.find()
        return user_list

    def find_one_by_username(self, username):
        '''获取指定数据'''
        user = self.users.find_one({"username": username})
        return user

    def find_many_by_name(self, name):
        '''获取指定数据'''
        # 正则方式模糊查询 + 类全文索引
        user_list = self.users.find({'$or': [{'name': {'$regex': name}}, {'nickname': {'$regex': name}}]})
        return user_list

    def insert_one(self, data):
        '''插入数据'''
        self.users.insert_one(data)

    def find_id(self, username):
        '''查找数据的obId'''
        user = self.users.find_one({"username": username})
        return user['_id']

    def insert_label(self, id):
        '''给没有labels的用户设置空labels'''
        if self.find_label(id) == None:
            self.users.update_one({"_id": ObjectId(id)}, {'$set': {'labels': {}}})

    def update_label(self, id, label, value):
        '''更新labels中label的值'''
        # 没有labels的用户首先设置label
        self.insert_label(id)
        # 首先找到对应用户的labels
        user = self.users.find_one({"_id": ObjectId(id)})
        cur_labels = user['labels']
        if cur_labels.has_key(label):
            cur_labels[label] = cur_labels[label] + value
        else:  # 新增对应label
            cur_labels[label] = value
        self.users.update_one({"_id": ObjectId(id)}, {'$set': {'labels': cur_labels}})

    # 根据id返回加密后的密码，用于在修改时的密码认证
    def get_password_by_id(self, id=None):
        if id == None:
            raise Exception('请提供 id 完整参数!')
        user = self.users.find_one({"_id": ObjectId(id)})
        return user['password']

    # 修改密码
    def changePassword(self, id=None, newPwd=None):
        if id == None or newPwd == None:
            raise Exception('请提供 id 和 密码 完整参数!')
        self.users.update_one({'_id': ObjectId(id)}, {'$set': {'password': newPwd}})

    # 修改出生日期
    def changeBirthday(self, id=None, newBirthday=None):
        if id == None or newBirthday == None:
            raise Exception('请提供 id 和 日期 完整参数!')
        self.users.update_one({'_id': ObjectId(id)}, {'$set': {'birthday': newBirthday}})

    # 添加病历
    def addMedicalRecord(self, id=None, data=None):
        if id == None or data == None:
            raise Exception('请提供 id 和 病历 完整参数!')
        user = self.users.find_one({"_id": ObjectId(id)})
        temp = list(user['medicalRecord'] or [''])
        temp = temp.append(data)
        self.users.update_one({'_id': ObjectId(id)}, {'$set': {'medicalRecord': temp}})