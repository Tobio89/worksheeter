import os
from datetime import datetime
from time import ctime

DOC_files_path = os.path.join('.', 'app', 'static', 'download')
# DOC_files_path = r'C:\Users\User\.spyder-py3\Flask\worksheet_maker\app\static\download'


def timeless(complete_datetime):

    return datetime(complete_datetime.year, complete_datetime.month, complete_datetime.day)


def makeCDate(f_ctime):
    conventional_format = ctime(f_ctime)
    complete_datetime = datetime.strptime(conventional_format, '%a %b %d %H:%M:%S %Y')

    return timeless(complete_datetime)

def clearOldFiles():

    file_list = os.listdir(DOC_files_path)
    now = datetime.today()
    today = datetime(now.year, now.month, now.day)

    for f in file_list:
        f_path = os.path.join(DOC_files_path, f)

        f_ctime = os.path.getctime(f_path)
        
        f_datetime = makeCDate(f_ctime)

        if f_datetime < today:
            # print('pretend to delete')
            os.remove(f_path)
# clearOldFiles()