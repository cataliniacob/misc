#!/usr/bin/env python
""" A horribly hackish script to do the grunt work for https://bugzilla.mozilla.org/show_bug.cgi?id=798914
Could be generalized in case I need something similar later
"""

import copy
import io
import itertools
import operator
import os
import re
import sys
import tempfile
import unittest

import clang.cindex

def has_top_level_using_directive(tu, namespace):
    def is_the_ns(cursor):
        return cursor.kind == clang.cindex.CursorKind.NAMESPACE_REF and cursor.displayname == namespace
    def has_ns_child(cursor):
        return any(itertools.imap(is_the_ns, cursor.get_children()))
    def is_using_ns(cursor):
        return cursor.kind == clang.cindex.CursorKind.USING_DIRECTIVE and has_ns_child(cursor)

    return any(itertools.imap(is_using_ns, tu.cursor.get_children()))



def insert_include(lines, header):
    incl_pat = re.compile(r'\s*[#]include\s+["<](?P<file>[a-zA-Z/.]+)[">]')
    pos_to_include = -1

    for pos, line in enumerate(lines):
        match = incl_pat.match(line)
        if match:
            included = match.group('file')
            if header == included:
                # found it
                return

            prefix = os.path.commonprefix([header, included])
            if '/' in prefix:
                if included > header:
                    pos_to_include = pos
                    break
                else:
                    pos_to_include = pos + 1
            if pos_to_include < 0:
                pos_to_include = pos

    if pos_to_include < 0:
        pos_to_include = 0
    lines.insert(pos_to_include, '#include "{}"\n'.format(header))


class BaseTestInsert(unittest.TestCase):
    def assert_inserted_at_pos(self, what, where):
        before_insertion = copy.deepcopy(self.lines)

        insert_include(self.lines, what)
        new = self.lines.index('#include "{}"\n'.format(what))
        self.assertEqual(new, where)

        del self.lines[new]
        self.assertEqual(self.lines, before_insertion)


class TestInsert(BaseTestInsert):
    def setUp(self):
        self.lines = ['#include "foo/bar.h"', # 0
                      '// a comment', # 1
                      '#include\t<cab/abcdef.h>', # 2
                      '#include "c/d.h"', # 3
                      ' \t', # 4
                      '#include\t<c/f.h>', # 5
                      '# include\t<cab/erty.h>', # 6
                      ' #include  "c/i.h"', # 7
                      ]


    def test_misc(self):
        self.assert_inserted_at_pos('hello.h', 0)
        self.assert_inserted_at_pos('xyz.h', 0)
        self.assert_inserted_at_pos('c/a.h', 3)
        self.assert_inserted_at_pos('c/e.h', 5)
        self.assert_inserted_at_pos('c/g.h', 7)
        self.assert_inserted_at_pos('c/jire.h', 8)
        self.assert_inserted_at_pos('foo/a.h', 0)

    def test_already_present(self):
        before_insertion = copy.deepcopy(self.lines)
        insert_include(self.lines, 'c/f.h')
        self.assertEqual(self.lines, before_insertion)

    def test_empty_includes(self):
        includes = []
        insert_include(includes, 'a/b.h')
        self.assertEqual(includes, ['#include "a/b.h"\n'])


class TestPrevPos(BaseTestInsert):
    def setUp(self):
        self.lines = ['#include "nsCategoryManagerUtils.h"',
                      '#include "xptiprivate.h"',
                      '#include "mozilla/XPTInterfaceInfoManager.h"',
                      ]

    def test_prev_pos(self):
        self.assert_inserted_at_pos('mozilla/MemoryReporting.h', 2)


class TestWithCommentsInTheBeginning(BaseTestInsert):
    def setUp(self):
        self.lines = ['// a comment in the beginning',
                      '#include "nsCategoryManagerUtils.h"',
                      ]

    def test_prev_pos(self):
        self.assert_inserted_at_pos('mozilla/MemoryReporting.h', 1)


def rename_type(path, replaced, replacement):
    _, ext = os.path.splitext(path)

    with io.open(path, 'rb') as f:
        tu_lines = f.readlines()

    if not any(itertools.imap(lambda line: replaced in line, tu_lines)):
        # no need to do parsing, we won't replace anything
        sys.exit(0)

    temp_tu = tempfile.NamedTemporaryFile(delete=False, suffix=ext) # the extension matters for libclang
    try:
        temp_tu.file.write('namespace mozilla {}\n')
        map(temp_tu.file.write, tu_lines)
        temp_tu.file.close()

        print 'parsing file {} derived from {}'.format(temp_tu.name, path)
        index = clang.cindex.Index.create()
        tu = index.parse(temp_tu.name, options=clang.cindex.TranslationUnit.PARSE_INCOMPLETE)

        if not has_top_level_using_directive(tu, 'mozilla'):
            replacement = 'mozilla::{}'.format(replacement)

        print 'replacing {} with {} and inserting include'.format(replaced, replacement)
        insert_include(tu_lines, 'mozilla/MemoryReporting.h')
        new_tu_lines = map(lambda line: line.replace(replaced, replacement), tu_lines)

        with io.open(path, 'wb') as f:
            map(f.write, new_tu_lines)
    finally:
        os.unlink(temp_tu.name)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # no args just test
        unittest.main()
    else:
        rename_type(sys.argv[1], 'nsMallocSizeOfFun', 'MallocSizeOf')
