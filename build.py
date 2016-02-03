#!/usr/bin/env python
from __future__ import print_function, unicode_literals
from subprocess import call

import os
import sys

import argparse
from nose.core import run


def lint():
    """
    run linter on our code base.
    """
    path = os.path.realpath(os.getcwd())
    cmd = 'flake8 %s' % path
    opt = ''
    print(">>> Linting codebase with the following command: %s %s" % (cmd, opt))

    try:
        return_code = call([cmd, opt], shell=True)
        if return_code < 0:
            print(">>> Terminated by signal", -return_code, file=sys.stderr)
        elif return_code != 0:
            sys.exit('>>> Lint checks failed')
        else:
            print(">>> Lint checks passed", return_code, file=sys.stderr)
    except OSError as e:
        print(">>> Execution failed:", e, file=sys.stderr)


def unit_test(extra_args=[]):
    """
    run unit tests for this code base. Pass any arguments that nose accepts.
    """
    path = os.path.realpath(os.path.join(os.getcwd(), 'tests/unit'))
    args = [
        path, '-x', '-v', '--with-coverage', '--cover-erase',
        '--cover-package=./build/lib/freight_forwarder',
        '--cover-package=./freight_forwarder'
    ]

    if extra_args:
        args.extend(extra_args)

    if run(argv=args):
        return 0
    else:
        return 1


def test_suite():
    """
    run both unit test and lint with default args

    Need to come back to add flags to allow multiple arugments to each
    unit_test and lint
    """
    lint()
    unit_test()


def main():
    """
    need to add http://sphinx-doc.org/
    """
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers()

    lint_parser = sub_parser.add_parser('lint')
    lint_parser.set_defaults(func=lint)

    unit_test_parser = sub_parser.add_parser('unit-test')
    unit_test_parser.set_defaults(func=unit_test)

    test_suite_parser = sub_parser.add_parser('test-suite')
    test_suite_parser.set_defaults(func=test_suite)

    args, extra_args = parser.parse_known_args()

    if extra_args:
        args.func(extra_args)
    else:
        args.func()


if __name__ == '__main__':
    main()
