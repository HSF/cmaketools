#!/usr/bin/env python
"""
Small script to execute a command in a modified environment (see man 1 env).
"""
import os

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

def parse_args():
    '''
    Parse the command line arguments.
    '''

    from optparse import OptionParser, OptionValueError

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

    parser = OptionParser(prog = "env.py",
                          usage = "Usage: %prog [OPTION]... [NAME=VALUE]... [COMMAND [ARG]...]",
                          description = "Set each NAME to VALUE in the environment and run COMMAND.",
                          epilog = "The operations are performed in the order they appear on the "
                                   "command line. If no COMMAND is provided, print the resulting "
                                   "environment. (Note: this command is modeled after the Unix "
                                   "command 'env', see \"man env\")" )

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
    parser.disable_interspersed_args()
    parser.set_defaults(actions=[], ignore_environment=False)

    return parser.parse_args()

def prepareEnv(ignore_system=False):
    '''
    Prepare an EnvConfig.Control instance to operate on the environment.

    @param ignore_system: if set to True, the system environment is ignored.
    '''
    from EnvConfig import Control
    control = Control.Environment()

    if not ignore_system:
        control.presetFromSystem()

    return control

def makeEnv(actions, ignore_system=False):
    '''
    Return a dictionary of the environment variables after applying the actions.

    @param ignore_system: if set to True, the system environment is ignored.
    '''
    # prepare initial control object
    control = prepareEnv(ignore_system)

    # apply al the actions
    for action, args in actions:
        apply(getattr(control, action), args)

    # extract the result env dictionary
    return control.vars()

def main():
    '''
    Main function of the script.
    '''

    opts, args = parse_args()

    cmd = []
    # find the (implicit) 'set' arguments in the list of arguments
    # and put the rest in the command
    try:
        for i, a in enumerate(args):
            opts.actions.append(('set', splitNameValue(a)))
    except EnvError:
        cmd = args[i:]

    if opts.shell and cmd:
        print >> sys.stderr, "Invalid arguments: --%s cannot be used with a command." % opts.shell
        return 2

    env = makeEnv(opts.actions, opts.ignore_environment)

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

    if not cmd:
        if opts.shell == 'py':
            from pprint import pprint
            pprint(env)
        else:
            template = {'sh':  "export %s='%s'",
                        'csh': "setenv %s '%s'"}.get(opts.shell, "%s=%s")
            for nv in sorted(env.items()):
                print template % nv
        return 0
    else:
        from subprocess import Popen
        return Popen(cmd, env=env).wait()

if __name__ == "__main__":
    import sys
    sys.exit(main())
