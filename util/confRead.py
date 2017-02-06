# -*- coding:utf-8 -*-
# desc: use to read ini  # #
# 实现一个配置文件读取模块，支持两种方式，一种是类的形式，一种是函数形式

import sys
import configparser

#类的形式
class Config:  
    def __init__(self, path):  
        self.path = path  
        self.cf = configparser .ConfigParser()
        self.cf.read(self.path)  
    def get(self, field, key):  
        result = ""  
        try:  
            result = self.cf.get(field, key)  
        except:  
            print("cannot find the value for: [%s:%s]" % (field,key))
            result = ""
        return result  
        
    def set(self, field, key, value):
        try:  
            self.cf.set(field, key, value)  
            self.cf.write(open(self.path,'w'))
        except:
            print("write configure failed!")
            return False  
        return True  
              
              
 
#函数形式
def read_config(config_file_path, field, key):   
    cf = configparser .ConfigParser()
    try:  
        cf.read(config_file_path)  
        result = cf.get(field, key)  
    except:
        print("cannot find the value for: [%s:%s]" % (field,key))
        sys.exit(1)  
    return result  
 
#读取该Section下的所有键值对
def read_configBySection(config_file_path, field):   
    cf = configparser .ConfigParser()
    try:  
        cf.read(config_file_path)  
        result = cf.items(field)  
    except:
        print("cannot find the section for: [%s]" % (field))
        sys.exit(1)  
    return result

    
def write_config(config_file_path, field, key, value):  
    cf = configparser .ConfigParser()
    try:  
        cf.read(config_file_path)  
        cf.set(field, key, value)  
        cf.write(open(config_file_path,'w'))  
    except:  
        sys.exit(1)  
    return True  

if __name__ == "__main__":  
    config_file_path = '../conf/config.ini'

    # 从配置文件中读取路径参数
    # hosts = read_configBySection(config_file_path, 'Server')
    # print(hosts)

    config  = Config(config_file_path)
    host = config.get('Server','host').strip()
    port = config.get('Server','port').strip()

    db_name = config.get('Database','db_name').strip()
    stock_collection = config.get('Database','stock_collection').strip()
    index_collection = config.get('Database','index_collection').strip()
    print(host,port)
    print(db_name,stock_collection,index_collection)