#!/usr/bin/env python

import os
import subprocess
import sys
import uuid

if __name__ == '__main__':
    dir_name = sys.argv[1]

    for root, dirs, files in os.walk(dir_name):
        for file_name in files:
            rand_name = uuid.uuid4().hex
            src = os.path.join(root, file_name)
            if src.endswith('.mp3'):
                subprocess.check_call(['eyeD3', '--artist', rand_name, '--album', rand_name, src])

            os.rename(src, os.path.join(root, '{} {}'.format(rand_name, file_name)))

