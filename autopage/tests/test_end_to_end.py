#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import itertools
import os
import unittest
import sys

from autopage.tests import isolation

import autopage


MAX_LINES_PER_PAGE = isolation.LINES - 1


def finite(num_lines, **kwargs):
    def finite():
        ap = autopage.AutoPager(**kwargs)
        with ap as out:
            for i in range(num_lines):
                print(i, file=out)
        return ap.exit_code()
    return finite


def infinite():
    ap = autopage.AutoPager()
    try:
        with ap as out:
            for i in itertools.count():
                print(i, file=out)
    except KeyboardInterrupt:
        pass
    return ap.exit_code()


def from_stdin():
    ap = autopage.AutoPager(line_buffering=autopage.line_buffer_from_input())
    with ap as out:
        try:
            for line in sys.stdin:
                print(line.rstrip(), file=out)
        except KeyboardInterrupt:
            pass
    return ap.exit_code()


def with_exception():
    class MyException(Exception):
        pass

    ap = autopage.AutoPager()
    try:
        with ap as out:
            for i in range(50):
                print(i, file=out)
            raise MyException()
    except MyException:
        pass
    return ap.exit_code()


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        os.environ['LESS_IS_MORE'] = '1'

    def test_page_to_end(self):
        num_lines = 100
        with isolation.isolate(finite(num_lines)) as env:
            pager = isolation.PagerControl(env)

            lines = num_lines
            while lines > 0:
                expected = min(lines, MAX_LINES_PER_PAGE)
                self.assertEqual(expected, pager.advance())
                lines -= expected
            self.assertEqual(0, pager.advance())
            self.assertEqual(0, pager.advance())
            self.assertEqual(0, pager.quit())

            self.assertEqual(num_lines, pager.total_lines())
        self.assertEqual(0, env.exit_code())

    def test_page_to_middle(self):
        num_lines = 100
        with isolation.isolate(finite(num_lines)) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())
            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())
            self.assertEqual(MAX_LINES_PER_PAGE, pager.quit())
        self.assertEqual(0, env.exit_code())

    def test_exit_pager_early(self):
        with isolation.isolate(infinite) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())
            self.assertEqual(MAX_LINES_PER_PAGE, pager.quit())
        self.assertEqual(141, env.exit_code())

    def test_interrupt_early(self):
        with isolation.isolate(infinite) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())
            env.interrupt()
            while pager.advance():
                continue
            pager.quit()
            self.assertGreater(pager.total_lines(), MAX_LINES_PER_PAGE)
        self.assertEqual(130, env.exit_code())

    def test_interrupt_early_quit(self):
        with isolation.isolate(infinite) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())
            env.interrupt()
            pager.quit()
            self.assertGreater(pager.total_lines(), MAX_LINES_PER_PAGE)
        self.assertEqual(130, env.exit_code())

    def test_interrupt_in_middle_after_complete(self):
        num_lines = 100
        with isolation.isolate(finite(num_lines)) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(MAX_LINES_PER_PAGE, pager.advance())

            for i in range(100):
                env.interrupt()

            self.assertEqual(MAX_LINES_PER_PAGE, pager.quit())
        self.assertEqual(0, env.exit_code())

    def test_interrupt_at_end_after_complete(self):
        num_lines = 100
        with isolation.isolate(finite(num_lines)) as env:
            pager = isolation.PagerControl(env)

            while pager.advance():
                continue

            self.assertEqual(num_lines, pager.total_lines())

            for i in range(100):
                env.interrupt()

            self.assertEqual(0, pager.quit())
        self.assertEqual(0, env.exit_code())

    def test_short_output(self):
        del os.environ['LESS_IS_MORE']
        num_lines = 10
        with isolation.isolate(finite(num_lines)) as env:
            pager = isolation.PagerControl(env)

            for i, l in enumerate(pager.read_lines(num_lines)):
                self.assertEqual(str(i), l.rstrip())
        self.assertEqual(0, env.exit_code())

    def test_short_output_reset(self):
        num_lines = 10
        with isolation.isolate(finite(num_lines, reset_on_exit=True)) as env:
            pager = isolation.PagerControl(env)

            self.assertEqual(num_lines, pager.quit())
        self.assertEqual(0, env.exit_code())

    def test_short_streaming_output(self):
        num_lines = 10
        r, w = os.pipe()
        with isolation.isolate(from_stdin, stdin_fd=r) as env:
            pager = isolation.PagerControl(env)

            with os.fdopen(w, 'w') as in_pipe:
                for i in range(num_lines):
                    print(i, file=in_pipe)

            for i, l in enumerate(pager.read_lines(num_lines)):
                self.assertEqual(i, int(l))

            env.interrupt()
            self.assertEqual(0, pager.quit())
        self.assertEqual(0, env.exit_code())

    def test_exception(self):
        num_lines = 50
        with isolation.isolate(with_exception) as env:
            pager = isolation.PagerControl(env)

            lines = num_lines
            while lines > 0:
                expected = min(lines, MAX_LINES_PER_PAGE)
                self.assertEqual(expected, pager.advance())
                lines -= expected
            self.assertEqual(0, pager.advance())
            self.assertEqual(0, pager.advance())
            self.assertEqual(0, pager.quit())

            self.assertEqual(num_lines, pager.total_lines())
        self.assertEqual(1, env.exit_code())
