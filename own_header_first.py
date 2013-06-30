#!/usr/bin/env python3

import copy
import functools
import operator
import os.path
import re
import sys

def move_include(lines, what, after_what):
    incl_pat = re.compile(r'\s*[#]include\s+["<](?P<file>[a-zA-Z/.]+)[">]')
    first_include_pos = None
    what_pos = None
    after_what_pos = None

    for pos, line in enumerate(lines):
        match = incl_pat.match(line)
        if match:
            if first_include_pos is None:
                first_include_pos = pos

            included = match.group('file')
            if included == what:
                what_pos = pos
            if (included == after_what) or (included.endswith('/{}'.format(after_what))):
                after_what_pos = pos

    if (what_pos is not None) and (after_what_pos is not None) and what_pos < after_what_pos:
        if first_include_pos != what_pos and first_include_pos != after_what_pos:
            print("First include is {0!r}, not something we're looking for".format(lines[first_include_pos]))
            return

        print('Found {} at {}'.format(what, what_pos))
        print('Found {} at {}'.format(after_what, after_what_pos))

        lines_between = lines[what_pos + 1:after_what_pos]
        if not all(map(functools.partial(operator.eq, '\n'), lines_between)):
            print('Found other lines between the two includes, not swapping: {}'.format(lines_between))
            return

        lines[what_pos], lines[after_what_pos] = lines[after_what_pos], lines[what_pos]

        try:
            what_after = lines[what_pos + 1]
        except IndexError:
            pass
        else:
            if what_after != '\n':
                lines.insert(what_pos + 1, '\n')
                after_what_pos = after_what_pos + 1 # we inserted a new thing, adjust this position

        try:
            what_after = lines[after_what_pos + 1]
        except IndexError:
            pass
        else:
            if what_after != '\n' and ('mozilla/' not in what_after):
                lines.insert(after_what_pos + 1, '\n')

if __name__ == '__main__':
    print('Processing {}'.format(sys.argv[1]))

    source = sys.argv[1]
    src_name, src_ext = os.path.splitext(source)
    if src_ext not in ['.c', '.cpp', '.mm']:
        print('Wrong file type "{}"'.format(src_ext), file=sys.stderr)
        sys.exit(1)
    header_name = '{}.h'.format(os.path.basename(src_name))

    with open(source, 'r', encoding='latin1') as f:
        lines = f.readlines()
    prev_lines = copy.copy(lines)
    move_include(lines, what='mozilla/MemoryReporting.h', after_what=header_name)
    if prev_lines != lines:
        with open(source, 'w', encoding='latin1') as f:
            list(map(f.write, lines))
