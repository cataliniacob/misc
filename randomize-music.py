#!/usr/bin/env python

import os
import subprocess
import sys
import uuid

if __name__ == '__main__':
    dir_name = sys.argv[1]

    for file_name in os.listdir(dir_name):
        rand_name = uuid.uuid4().hex
        src = os.path.join(dir_name, file_name)
        subprocess.check_call(['eyeD3', '--artist', rand_name, '--album', rand_name, src])

        os.rename(src, os.path.join(dir_name, '{} {}'.format(rand_name, file_name)))

