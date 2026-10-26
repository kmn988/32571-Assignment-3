import os
from configparser import ConfigParser
from helper.helper_web import get_helper

def before_all(context):
    config = ConfigParser()
    my_file = os.path.join(os.getcwd(), 'setup.cfg')
    config.read(my_file)

    helper_func = get_helper(config.get('Environment', 'Browser'))
    context.helper = helper_func
    context.session = {"user": None}

def after_all(context):
    context.helper.close()