import os
from sounds import shout


class Logger:
    dir_name = 'temp'
    file_name = 'log.txt'

    def __init__(self):
        self.log_list = []
        dir_name = self.dir_name
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        self.fpath = os.path.join(dir_name, self.file_name)
        with open(self.fpath, 'w') as f:
            f.write('')

    def add(self, msg):
        msg = str(msg)
        self.log_list.append(msg)
        with open(self.fpath, 'a') as f:
            f.write(msg + '\n')

    def show(self, msg):
        print(msg)
        self.add(msg)

    def shout(self, msg):
        shout(msg)
        self.add(msg)

    def confirm(self, msg):
        print(msg)
        input('Press Enter to proceed:')

    def view(self):
        self.confirm('\n'.join(self.log_list))
