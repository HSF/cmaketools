__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import os
import sys
assert sys.version_info >= (2, 6), "Python 2.6 required"

import logging

__all__ = []

# Prepare the search path for environment XML files
path = ['.']
if 'ENVXMLPATH' in os.environ:
    path.extend(os.environ['ENVXMLPATH'].split(os.pathsep))

import Control

class EnvError(RuntimeError):
    '''
    Simple class to wrap errors in the environment configuration.
    '''
    pass

def splitNameValue(name_value):
    """split the "NAME=VALUE" string into the tuple ("NAME", "VALUE")
    replacing '[:]' with os.pathsep in VALUE"""
    if '=' not in name_value:
        raise EnvError("Invalid variable argument '%s'." % name_value)
    n, v = name_value.split('=', 1)
    return n, v.replace('[:]', os.pathsep)

class Script(object):
    '''
    Environment Script class used to control the logic of the script and allow
    extensions.
    '''
    __usage__  = "Usage: %prog [OPTION]... [NAME=VALUE]... [COMMAND [ARG]...]"
    __desc__   = "Set each NAME to VALUE in the environment and run COMMAND."
    __epilog__ = ("The operations are performed in the order they appear on the "
                  "command line. If no COMMAND is provided, print the resulting "
                  "environment. (Note: this command is modeled after the Unix "
                  "command 'env', see \"man env\")")
    def __init__(self, args=None):
        '''
        Initializes the script instance parsing the command line arguments (or
        the explicit arguments provided).
        '''
        self.parser = None
        self.opts = None
        self.cmd = None
        self.control = None
        self.log = None
        self.env = {}
        # Run the core code of the script
        self._prepare_parser()
        self._parse_args(args)
        self._check_args()

    def _prepare_parser(self):
        '''
        Prepare an OptionParser instance used to analyze the command line
        options and arguments.
        '''
        from optparse import OptionParser, OptionValueError
        parser = OptionParser(prog=os.path.basename(sys.argv[0]),
                              usage=self.__usage__,
                              description=self.__desc__,
                              epilog=self.__epilog__)
        self.log = logging.getLogger(parser.prog)

        def addOperation(option, opt, value, parser, action):
            '''
            Append to the list of actions the tuple (action, (<args>, ...)).
            '''
            if action not in ('unset', 'loadXML'):
                try:
                    value = splitNameValue(value)
                except EnvError:
                    raise OptionValueError("Invalid value for option %s: '%s', it requires NAME=VALUE." % (opt, value))
            else:
                value = (value,)
            parser.values.actions.append((action, value))

        parser.add_option("-i", "--ignore-environment",
                          action="store_true",
                          help="start with an empty environment")
        parser.add_option("-u", "--unset",
                          metavar="NAME",
                          action="callback", callback=addOperation,
                          type="str", nargs=1, callback_args=('unset',),
                          help="remove variable from the environment")
        parser.add_option("-s", "--set",
                          metavar="NAME=VALUE",
                          action="callback", callback=addOperation,
                          type="str", nargs=1, callback_args=('set',),
                          help="set the variable NAME to VALUE")
        parser.add_option("-a", "--append",
                          metavar="NAME=VALUE",
                          action="callback", callback=addOperation,
                          type="str", nargs=1, callback_args=('append',),
                          help="append VALUE to the variable NAME (with a '%s' as separator)" % os.pathsep)
        parser.add_option("-p", "--prepend",
                          metavar="NAME=VALUE",
                          action="callback", callback=addOperation,
                          type="str", nargs=1, callback_args=('prepend',),
                          help="prepend VALUE to the variable NAME (with a '%s' as separator)" % os.pathsep)
        parser.add_option("-x", "--xml",
                          action="callback", callback=addOperation,
                          type="str", nargs=1, callback_args=('loadXML',),
                          help="XML file describing the changes to the environment")
        parser.add_option("--sh",
                          action="store_const", const="sh", dest="shell",
                          help="Print the environment as shell commands for 'sh'-derived shells.")
        parser.add_option("--csh",
                          action="store_const", const="csh", dest="shell",
                          help="Print the environment as shell commands for 'csh'-derived shells.")
        parser.add_option("--py",
                          action="store_const", const="py", dest="shell",
                          help="Print the environment as Python dictionary.")

        parser.add_option('--verbose', action='store_const',
                          const=logging.INFO, dest='log_level',
                          help='print more information')
        parser.add_option('--debug', action='store_const',
                          const=logging.DEBUG, dest='log_level',
                          help='print debug messages')
        parser.add_option('--quiet', action='store_const',
                          const=logging.WARNING, dest='log_level',
                          help='print only warning messages (default)')

        parser.disable_interspersed_args()
        parser.set_defaults(actions=[],
                            ignore_environment=False,
                            log_level=logging.WARNING)

        self.parser = parser

    def _parse_args(self, args=None):
        '''
        Parse the command line arguments.
        '''
        opts, args = self.parser.parse_args(args)

        # set the logging level
        logging.basicConfig(level=opts.log_level)

        cmd = []
        # find the (implicit) 'set' arguments in the list of arguments
        # and put the rest in the command
        try:
            for i, a in enumerate(args):
                opts.actions.append(('set', splitNameValue(a)))
        except EnvError:
            cmd = args[i:]

        self.opts, self.cmd = opts, cmd

    def _check_args(self):
        '''
        Check consistency of command line options and arguments.
        '''
        if self.opts.shell and self.cmd:
            self.parser.error("Invalid arguments: --%s cannot be used with a command." % self.opts.shell)

    def _makeEnv(self):
        '''
        Generate a dictionary of the environment variables after applying all
        the required actions.
        '''
        # prepare the environment control instance
        control = Control.Environment()
        if not self.opts.ignore_environment:
            control.presetFromSystem()

        # apply all the actions
        for action, args in self.opts.actions:
            apply(getattr(control, action), args)

        # extract the result env dictionary
        env = control.vars()

        # set the library search path correctly for the non-Linux platforms
        if "LD_LIBRARY_PATH" in env:
            # replace LD_LIBRARY_PATH with the corresponding one on other systems
            if sys.platform.startswith("win"):
                other = "PATH"
            elif sys.platform.startswith("darwin"):
                other = "DYLD_LIBRARY_PATH"
            else:
                other = None
            if other:
                if other in env:
                    env[other] = env[other] + os.pathsep + env["LD_LIBRARY_PATH"]
                else:
                    env[other] = env["LD_LIBRARY_PATH"]
                del env["LD_LIBRARY_PATH"]

        self.env = env

    def dump(self):
        '''
        Print to standard output the final environment in the required format.
        '''
        if self.opts.shell == 'py':
            from pprint import pprint
            pprint(self.env)
        else:
            template = {'sh':  "export %s='%s'",
                        'csh': "setenv %s '%s'"}.get(self.opts.shell, "%s=%s")
            for nv in sorted(self.env.items()):
                print template % nv

    def runCmd(self):
        '''
        Execute a command in the modified environment and return the exit code.
        '''
        from subprocess import Popen
        return Popen(self.cmd, env=self.env).wait()

    def main(self):
        '''
        Main function of the script.
        '''
        self._makeEnv()
        if not self.cmd:
            self.dump()
        else:
            sys.exit(self.runCmd())
