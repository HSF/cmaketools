'''
Created on Jun 27, 2011

@author: mplajner
'''
import xmlModule
import os
from time import gmtime, strftime
import Variable

class Environment():
    '''object to hold settings of environment'''

    def __init__(self, loadFromSystem=True, useAsWriter=False, reportLevel=1, searchPath=None):
        '''Initial variables to be pushed and setup

        append switch between append and prepend for initial variables.
        loadFromSystem causes variable`s system value to be loaded on first encounter.
        If useAsWriter == True than every change to variables is recorded to XML file.
        reportLevel sets the level of messaging.
        '''
        self.report = xmlModule.Report(reportLevel)

        self.separator = ':'

        # Prepeare the internal search path for xml files (used by 'include' elements)
        self.searchPath = ['.']
        if searchPath is not None:
            self.searchPath.extend(searchPath)
        try:
            self.searchPath.extend(os.environ['ENVXMLPATH'].split(os.pathsep))
        except KeyError:
            # ignore if the env variable is not there
            pass

        self.actions = {}
        self.actions['include'] = lambda n, c, h: self.loadXML(self._locate(n, c, h))
        self.actions['append'] = lambda n, v, _: self.append(n, v)
        self.actions['prepend'] = lambda n, v, _: self.prepend(n, v)
        self.actions['set'] = lambda n, v, _: self.set(n, v)
        self.actions['unset'] = lambda n, v, _: self.unset(n, v)
        self.actions['default'] = lambda n, v, _: self.default(n, v)
        self.actions['remove'] = lambda n, v, _: self.remove(n, v)
        self.actions['remove-regexp'] = lambda n, v, _: self.remove_regexp(n, v)
        self.actions['declare'] = self.declare

        self.variables = {}

        self.loadFromSystem = loadFromSystem
        self.asWriter = useAsWriter
        if useAsWriter:
            self.writer = xmlModule.XMLFile()
            self.startXMLinput()

        self.loadedFiles = set()

        # Prepare the stack for the directory of the loaded file(s)
        self._fileDirStack = []
        # Note: cannot use self.declare() because we do not want to write out
        #       the changes to ${.}
        dot = Variable.Scalar('.', local=True, report=self.report)
        dot.expandVars = False
        dot.set('')
        self.variables['.'] = dot


    def _locate(self, filename, caller=None, hints=None):
        '''
        Find 'filename' in the internal search path.
        '''
        from os.path import isabs, isfile, join, dirname, normpath, abspath
        if isabs(filename):
            return filename

        if hints is None:
            hints = []
        elif type(hints) is str:
            hints = hints.split(self.separator)

        if caller:
            calldir = dirname(caller)
            localfile = join(calldir, filename)
            if isfile(localfile):
                return localfile
            # allow for relative hints
            hints = [join(calldir, hint) for hint in hints]

        try:
            return (abspath(f)
                    for f in [normpath(join(d, filename))
                              for d in self.searchPath + hints]
                    if isfile(f)).next()
        except StopIteration:
            from errno import ENOENT
            raise OSError(ENOENT, 'cannot find file in %r' % self.searchPath, filename)

    def vars(self, strings=True):
        '''returns dictionary of all variables optionally converted to string'''
        if strings:
            return dict([(n, v.value(True)) for n, v in self.variables.items()])
        else:
            return self.variables

    def var(self, name):
        '''Gets a single variable. If not available then tries to load from system.'''
        if name in self.variables:
            return self.variables[name]
        else:
            return os.environ[name]

    def search(self, varName, expr, regExp=False):
        '''Searches in a variable for a value.'''
        return self.variables[varName].search(expr, regExp)

    def _guessType(self, varname):
        '''
        Guess the type of the variable from its name: if the name contains
        'PATH' or 'DIRS', then the variable is a list, otherwise it is a scalar.
        '''
        varname = varname.upper() # make the comparison case insensitive
        if 'PATH' in varname or 'DIRS' in varname:
            return 'list'
        else:
            return 'scalar'

    def declare(self, name, vartype, local):
        '''Creates an instance of new variable. It loads values from the OS if the variable is not local.'''
        if self.asWriter:
            self._writeVarToXML(name, 'declare', '', vartype, local)

        if not isinstance(local, bool):
            if str(local).lower() == 'true':
                local = True
            else:
                local = False

        if name in self.variables.keys():
            if self.variables[name].local != local:
                raise Variable.EnvError(name, 'redeclaration')
            else:
                if vartype.lower() == "list":
                    if not isinstance(self.variables[name],Variable.List):
                        raise Variable.EnvError(name, 'redeclaration')
                else:
                    if not isinstance(self.variables[name],Variable.Scalar):
                        raise Variable.EnvError(name, 'redeclaration')

        if vartype.lower() == "list":
            a = Variable.List(name, local, report=self.report)
        else:
            a = Variable.Scalar(name, local, report=self.report)

        if self.loadFromSystem and not local and name in os.environ:
            a.expandVars = False # disable var expansion when importing from the environment
            a.set(os.environ[name], os.pathsep, environment=self.variables)
            a.expandVars = True

        self.variables[name] = a

    def append(self, name, value):
        '''Appends to an existing variable.'''
        if self.asWriter:
            self._writeVarToXML(name, 'append', value)
        else:
            if name not in self.variables:
                self.declare(name, self._guessType(name), False)
            self.variables[name].append(value, self.separator, self.variables)

    def prepend(self, name, value):
        '''Prepends to an existing variable, or create a new one.'''
        if self.asWriter:
            self._writeVarToXML(name, 'prepend', value)
        else:
            if name not in self.variables:
                self.declare(name, self._guessType(name), False)
            self.variables[name].prepend(value, self.separator, self.variables)

    def set(self, name, value):
        '''Sets a single variable - overrides any previous value!'''
        name = str(name)
        if self.asWriter:
            self._writeVarToXML(name, 'set', value)
        else:
            if name not in self.variables:
                self.declare(name, self._guessType(name), False)
            self.variables[name].set(value, self.separator, self.variables)

    def default(self, name, value):
        '''Sets a single variable only if it is not already set!'''
        name = str(name)
        if self.asWriter:
            self._writeVarToXML(name, 'default', value)
        else:
            # Here it is different from the other actions because after a 'declare'
            # we cannot tell if the variable was already set or not.
            # FIXME: improve declare() to allow for a default.
            if name not in self.variables:
                if self._guessType(name) == 'list':
                    v = Variable.List(name, False, report=self.report)
                else:
                    v = Variable.Scalar(name, False, report=self.report)
                if self.loadFromSystem and name in os.environ:
                    v.set(os.environ[name], os.pathsep, environment=self.variables)
                else:
                    v.set(value, self.separator, environment=self.variables)
                self.variables[name] = v
            else:
                v = self.variables[name]
                if not v.val:
                    v.set(value, self.separator, environment=self.variables)

    def unset(self, name, value=None):# pylint: disable=W0613
        '''Unsets a single variable to an empty value - overrides any previous value!'''
        if self.asWriter:
            self._writeVarToXML(name, 'unset', '')
        else:
            if name in self.variables:
                del self.variables[name]

    def remove(self, name, value, regexp=False):
        '''Remove value from variable.'''
        if self.asWriter:
            self._writeVarToXML(name, 'remove', value)
        else:
            if name not in self.variables:
                self.declare(name, self._guessType(name), False)
            self.variables[name].remove(value, self.separator, regexp)

    def remove_regexp(self, name, value):
        self.remove(name, value, True)


    def searchFile(self, filename, varName):
        '''Searches for appearance of variable in a file.'''
        XMLFile = xmlModule.XMLFile()
        variable = XMLFile.variable(filename, name=varName)
        return variable

    def loadXML(self, fileName=None, namespace='EnvSchema'):
        '''Loads XML file for input variables.'''
        XMLfile = xmlModule.XMLFile()
        fileName = self._locate(fileName)
        if fileName in self.loadedFiles:
            return # ignore recursion
        self.loadedFiles.add(fileName)
        dot = self.variables['.']
        # push the previous value of ${.} onto the stack...
        self._fileDirStack.append(dot.value())
        # ... and update the variable
        dot.set(os.path.dirname(fileName))
        variables = XMLfile.variable(fileName, namespace=namespace)
        for i, (action, args) in enumerate(variables):
            if action not in self.actions:
                self.report.addError('Node {0}: No action taken with var "{1}". Probably wrong action argument: "{2}".'.format(i, args[0], action))
            else:
                self.actions[action](*args) # pylint: disable=W0142
        # restore the old value of ${.}
        dot.set(self._fileDirStack.pop())
        # ensure that a change of ${.} in the file is reverted when exiting it
        self.variables['.'] = dot

    def startXMLinput(self):
        '''Renew writer for new input.'''
        self.writer.resetWriter()


    def finishXMLinput(self, outputFile = ''):
        '''Finishes input of XML file and closes the file.'''
        self.writer.writeToFile(outputFile)


    def writeToFile(self, fileName, shell='sh'):
        '''Creates an output file with a specified name to be used for setting variables by sourcing this file'''
        f = open(fileName, 'w')
        if shell == 'sh':
            f.write('#!/bin/bash\n')
            for variable in self.variables:
                if not self[variable].local:
                    f.write('export ' +variable+'='+self[variable].value(True, os.pathsep)+'\n')
        elif shell == 'csh':
            f.write('#!/bin/csh\n')
            for variable in self.variables:
                if not self[variable].local:
                    f.write('setenv ' +variable+' '+self[variable].value(True, os.pathsep)+'\n')
        else:
            f.write('')
            f.write('REM This is an enviroment settings file generated on '+strftime("%a, %d %b %Y %H:%M:%S\n", gmtime()))
            for variable in self.variables:
                if not self[variable].local:
                    f.write('set '+variable+'='+self[variable].value(True, os.pathsep)+'\n')

        f.close()


    def writeToXMLFile(self, fileName):
        '''Writes the current state of environment to a XML file.

        NOTE: There is no trace of actions taken, variables are written with a set action only.
        '''
        writer = xmlModule.XMLFile()
        for varName in self.variables:
            if varName == '.':
                continue # this is an internal transient variable
            writer.writeVar(varName, 'set', self.variables[varName].value(True, self.separator))
        writer.writeToFile(fileName)


    def presetFromSystem(self):
        '''Loads all variables from the current system settings.'''
        for k, v in os.environ.items():
            if k not in self.variables:
                self.set(k, v)

    def process(self):
        '''
        Call the variable processors on all the variables.
        '''
        for v in self.variables.values():
            v.val = v.process(val, self.variables)

    def _concatenate(self, value):
        '''Returns a variable string with separator separator from the values list'''
        stri = ""
        for it in value:
            stri += it + self.separator
        stri = stri[0:len(stri)-1]
        return stri


    def _writeVarToXML(self, name, action, value, vartype='list', local='false'):
        '''Writes single variable to XML file.'''
        if isinstance(value, list):
            value = self._concatenate(value)
        self.writer.writeVar(name, action, value, vartype, local)


    def __getitem__(self, key):
        return self.variables[key]

    def __setitem__(self, key, value):
        if key in self.variables.keys():
            self.report.addWarn('Addition canceled because of duplicate entry. Var: "' + key + '" value: "' + value + '".')
        else:
            self.append(key, value)

    def __delitem__(self, key):
        del self.variables[key]

    def __iter__(self):
        for i in self.variables:
            yield i

    def __contains__(self, item):
        return item in self.variables.keys()

    def __len__(self):
        return len(self.variables.keys())

