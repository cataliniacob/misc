#!/usr/bin/env python3
'''Make all files in a directory suitable for copying to a FAT filesystem.
'''

from __future__ import print_function

import os
import os.path
import sys

from six import u

if __name__ == u('__main__'):
    if len(sys.argv) != 2:
        print(u('Usage: {} <directory to make FAT ready>').format(sys.argv[0]),
              file=sys.stderr)
        sys.exit(1)

    fat_ready_dir = sys.argv[1]
    for root, dirs, files in os.walk(fat_ready_dir):
        for name in files:
            if u(':') in name:
                new_name = name.replace(u(':'), u(' '))

                full_path_old = os.path.join(root, name)
                full_path_new = os.path.join(root, new_name)

                print(u('Renaming {} to {}').format(full_path_old, full_path_new))
                os.rename(full_path_old, full_path_new)
