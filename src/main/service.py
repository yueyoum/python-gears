import os
import datetime

import memcache

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_PATH = os.path.normpath(os.path.join(CURRENT_PATH, '..'))
PROJECT_PATH = os.path.normpath(os.path.join(SRC_PATH, '..'))
RUN_PATH = os.path.join(PROJECT_PATH, 'run')


class Log(object):
    """used for logging errors, log file located in PROJECT/run folder"""
    
    def __init__(self, log_name='no_name.log'):
        _path = os.path.join(RUN_PATH, log_name)
        self.f = open(_path, 'a')
        self.write('********** start **********')
        
    
    @property
    def now_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(),
                                          '%Y-%m-%d %H:%M:%S')
        
    def write(self, msg):
        self.f.write('{0}: {1}\n'.format(self.now_time, msg))
        self.f.flush()
        
    def close(self):
        self.f.close()




def singleton(cls):
    instance = {}
    def get_instance():
        if cls not in instance:
            instance[cls] = cls()
        return instance[cls]
    return get_instance


@singleton
class MemcacheClient(object):
    def __init__(self, addr='127.0.0.1', port=11211, debug=0):
        self.c = memcache.Client(['{0}:{1}'.format(addr, port)], debug=debug)
        
    def set(self, key, value, time):
        self.c.set(key, value, time=time)
        
    def get(self, key):
        return self.c.get(key)
