'''
Created on Jul 2, 2011

@author: mplajner
'''

from xml.dom import minidom
import Variable
import logging.config
import os
from cPickle import load, dump
from hashlib import md5 # pylint: disable=E0611

class XMLFile():
    '''Takes care of XML file operations such as reading and writing.'''

    def __init__(self):
        self.xmlResult = '<?xml version="1.0" encoding="UTF-8"?><env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">\n'
        self.declaredVars = []
        logConf = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/log.conf')
        if not logging.getLogger('envLogger').handlers and os.path.exists(logConf):
            logging.config.fileConfig(logConf)
        self.logger = logging.getLogger('envLogger')

    def variable(self, path, namespace='EnvSchema', name=None):
        '''Returns list containing name of variable, action and value.

        @param path: a file name or a file-like object

        If no name given, returns list of lists of all variables and locals(instead of action 'local' is filled).
        '''
        isFilename = type(path) is str
        if isFilename:
            checksum = md5()
            checksum.update(open(path, 'rb').read())
            checksum = checksum.digest()

            cpath = path + "c" # preparsed file
            try:
                f = open(cpath, 'rb')
                oldsum, data = load(f)
                if oldsum == checksum:
                    return data
            except IOError:
                pass
            except EOFError:
                pass

            caller = path
        else:
            caller = None

        # Get file
        doc = minidom.parse(path)
        if namespace == '':
            namespace = None

        ELEMENT_NODE = minidom.Node.ELEMENT_NODE
        # Get all variables
        nodes = doc.getElementsByTagNameNS(namespace, "config")[0].childNodes
        variables = []
        for node in nodes:
            # if it is an element node
            if node.nodeType == ELEMENT_NODE:
                action = str(node.localName)

                if action == 'include':
                    if node.childNodes:
                        value = str(node.childNodes[0].data)
                    else:
                        value = ''
                    variables.append((action, (value, caller, str(node.getAttribute('hints')))))

                else:
                    varname = str(node.getAttribute('variable'))
                    if name and varname != name:
                        continue

                    if action == 'declare':
                        variables.append((action, (varname, str(node.getAttribute('type')), str(node.getAttribute('local')))))
                    else:
                        if node.childNodes:
                            value = str(node.childNodes[0].data)
                        else:
                            value = ''
                        variables.append((action, (varname, value, None)))

        if isFilename:
            try:
                f = open(cpath, 'wb')
                dump((checksum, variables), f, protocol=2)
                f.close()
            except IOError:
                pass
        return variables


    def resetWriter(self):
        '''resets the buffer of writer'''
        self.xmlResult = '<?xml version="1.0" encoding="UTF-8"?><env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">\n'
        self.declaredVars = []

    def writeToFile(self, outputFile=None):
        '''Finishes the XML input and writes XML to file.'''
        if outputFile is None:
            raise IOError("No output file given")
        self.xmlResult += '</env:config>'

        doc = minidom.parseString(self.xmlResult)
        with open(outputFile, "w") as f:
            f.write( doc.toxml() )

        f.close()
        return outputFile

    def writeVar(self, varName, action, value, vartype='list', local=False):
        '''Writes a action to a file. Declare undeclared elements (non-local list is default type).'''
        if action == 'declare':
            self.xmlResult += '<env:declare variable="'+varName+'" type="'+ vartype.lower() +'" local="'+(str(local)).lower()+'" />\n'
            self.declaredVars.append(varName)
            return

        if varName not in self.declaredVars:
            self.xmlResult += '<env:declare variable="'+varName+'" type="'+ vartype +'" local="'+(str(local)).lower()+'" />\n'
            self.declaredVars.append(varName)
        self.xmlResult += '<env:'+action+' variable="'+ varName +'">'+value+'</env:'+action+'>\n'


class Report():
    '''This class is used to catch errors and warnings from XML file processing to allow better managing and testing.'''

    # Sequence of levels: warn - warning - info - error
    def __init__(self, level = 1, reportOutput = False):
        self.errors = []
        self.warns = []
        self.info = []
        self.warnings = []
        self.level = level

        if not reportOutput:
            self.reportOutput = None
        else:
            self.reportOutput = open(reportOutput, 'w')

        logConf = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/log.conf')
        if not logging.getLogger('envLogger').handlers and os.path.exists(logConf):
            logging.config.fileConfig(logConf)
        self.logger = logging.getLogger('envLogger')

    def addError(self, message, varName = '', action = '', varValue = '', procedure = ''):
        error = [message, varName, action, varValue, procedure]
        if self.level < 4:
            if not self.reportOutput:
                print 'Error: ' + error[0]
            else:
                self.reportOutput.write('Error: ' + error[0] + '\n')
        self.errors.append(error)
        self.logger.error(message)

    def addWarn(self, message, varName = '', action = '', varValue = '', procedure = ''):
        error = [message, varName, action, varValue, procedure]
        if self.level < 1:
            if not self.reportOutput:
                print 'Warn: ' + error[0]
            else:
                self.reportOutput.write('Warn: ' + error[0] + '\n')
        self.warns.append(error)
        self.logger.warn(message)

    def addWarning(self, message, varName = '', action = '', varValue = '', procedure = ''):
        error = [message, varName, action, varValue, procedure]
        if self.level < 2:
            if not self.reportOutput:
                print 'Warning: ' + error[0]
            else:
                self.reportOutput.write('Warning: ' + error[0] + '\n')
        self.warnings.append(error)
        self.logger.warning(message)

    def addInfo(self, message, varName = '', action = '', varValue = '', procedure = ''):
        error = [message, varName, action, varValue, procedure]
        if self.level < 3:
            if not self.reportOutput:
                print 'Info: ' + error[0]
            else:
                self.reportOutput.write('Info: ' + error[0] + '\n')
        self.warnings.append(error)
        self.logger.info(message)

    def clear(self):
        self.errors = []
        self.warns = []
        self.info = []
        self.warnings = []

    def closeFile(self):
        if self.reportOutput:
            self.reportOutput.close()

    def numErrors(self):
        return len(self.errors)

    def numWarnings(self):
        return len(self.warns) + len(self.warnings)

    def error(self, key):
        return self.errors[key]

    def warn(self, key):
        return self.warns[key]


class XMLOperations():
    '''This class is for checking and merging XML files.

    Variables are stored in a double dictionary with keys of names and then actions.
    '''
    def __init__(self, separator=':', reportLevel=0, reportOutput=None):
        self.posActions = ['append','prepend','set','unset', 'remove', 'remove-regexp', 'declare']
        self.separator = separator
        self.report = Report(reportLevel, reportOutput=reportOutput)
        self.varNames = []
        self.realVariables = {}
        self.variables = {}
        self.file = None
        self.output = None

    def errors(self):
        return self.report.numErrors()

    def warnings(self):
        return self.report.numWarnings()

    def check(self, xmlFile):
        '''Runs a check through file

        First check is made on wrong action parameter.
        All valid actions are checked after and duplicated variables as well.
        '''
        #self.local = Variable.Local()
        # reset state
        self.varNames = []
        self.realVariables = {}
        self.variables = {}

        # load variables and resolve references to locals and then variables
        self._loadVariables(xmlFile)

        # report
        if (self.warnings() > 0 or self.errors() > 0):
            self.report.addInfo('Encountered '+ (str)(self.warnings()) +' warnings and ' + (str)(self.errors()) + ' errors.')
            return [self.warnings(), self.errors()]
        else:
            return True

        self.report.closeFile()


    def merge(self, xmlDoc1, xmlDoc2, outputFile = '', reportCheck = False):
        '''Merges two files together. Files are checked first during variables loading process.

        Second file is processed first, then the first file and after that they are merged together.
        '''
        self.output = outputFile
        self.file = XMLFile()
        self.variables = {}

        variables = self.file.variable(xmlDoc1)
        self._processVars(variables)
        variables = self.file.variable(xmlDoc2)
        self._processVars(variables)

        if not reportCheck:
            self.report.level = 5

        self.file.writeToFile(outputFile)

        self.report.addInfo('Files merged. Running check on the result.')
        self.check(self.output)
        self.report.closeFile()

    def _processVars(self, variables):
        for action, (arg1, arg2, arg3) in variables:
            if action == 'declare':
                if arg1 in self.variables.keys():
                    if arg2.lower() != self.variables[arg1][0]:
                        raise Variable.EnvError(arg1, 'redeclaration')
                    else:
                        if arg3.lower() != self.variables[arg1][1]:
                            raise Variable.EnvError(arg1, 'redeclaration')
                else:
                    self.file.writeVar(arg1, 'declare', '', arg2, arg3)
                    self.variables[arg1] = [arg2.lower(), arg3.lower()]
            else:
                self.file.writeVar(arg1, action, arg2)


    def _checkVariable(self, varName, action, local, value, nodeNum):# pylint: disable=W0613
        '''Tries to add to variables dict, checks for errors during process'''

        if varName not in self.variables:
            self.variables[varName] = []
            self.variables[varName].append(action)

        # If variable is in dict, check if this is not an unset command
        elif action == 'unset':
            if 'unset' in self.variables[varName]:
                self.report.addWarn('Multiple "unset" actions found for variable: "'+varName+'".', varName, 'multiple unset','', 'checkVariable')
            if not('unset' in self.variables[varName] and len(self.variables[varName]) == 1):
                self.report.addError('Node '+str(nodeNum)+': "unset" action found for variable "'+varName+'" after previous command(s). Any previous commands are overridden.', varName, 'unset overwrite')

        # or set command
        elif action == 'set':
            if len(self.variables[varName]) == 1 and 'unset' in self.variables[varName]:
                self.report.addWarn('Node '+str(nodeNum)+': "set" action found for variable "'+varName+'" after unset. Can be merged to one set only.')
            else:
                self.report.addError('Node '+str(nodeNum)+': "set" action found for variable "'+varName+'" after previous command(s). Any previous commands are overridden.', varName, 'set overwrite')
                if 'set' in self.variables[varName]:
                    self.report.addWarn('Multiple "set" actions found for variable: "'+varName+'".', varName, 'multiple set','', 'checkVariable')

        if action not in self.variables[varName]:
            self.variables[varName].append(action)

        try:
            if action == 'remove-regexp':
                action = 'remove_regexp'
            eval('(self.realVariables[varName]).'+action+'(value)')
        except Variable.EnvError as e:
            if e.code == 'undefined':
                self.report.addWarn('Referenced variable "' +e.val+ '" is not defined.')
            elif e.code == 'ref2var':
                self.report.addError('Reference to list from the middle of string.')
            elif e.code == 'redeclaration':
                self.report.addError('Redeclaration of variable "'+e.val+'".')
            else:
                self.report.addError('Unknown environment error occured.')


    def _loadVariables(self, fileName):
        '''loads XML file for input variables'''
        XMLfile = XMLFile()
        variables = XMLfile.variable(fileName)
        for i, (action, (arg1, arg2, arg3))  in enumerate(variables):
            undeclared = False
            if arg1 == '':
                raise RuntimeError('Empty variable or local name is not allowed.')

            if arg1 not in self.realVariables.keys():
                if action != 'declare':
                    self.report.addInfo('Node '+str(i)+': Variable '+arg1+' is used before declaration. Treated as an unlocal list furthermore.')
                    undeclared = True
                    self.realVariables[arg1] = Variable.List(arg1, False, report=self.report)
                else:
                    self.varNames.append(arg1)
                    if arg2 == 'list':
                        self.realVariables[arg1] = Variable.List(arg1, arg3, report=self.report)
                    else:
                        self.realVariables[arg1] = Variable.Scalar(arg1, arg3, report=self.report)
                    if not undeclared:
                        continue

            if action not in self.posActions:
                self.report.addError('Node '+str(i)+': Action "'+action+'" which is not implemented found. Variable "'+arg1+'".', arg1, action, arg2)
                continue

            else:
                if action == 'declare':
                    self.report.addError('Node '+str(i)+': Variable '+arg1+' is redeclared.')
                else:
                    self._checkVariable(arg1, action, self.realVariables[arg1].local, str(arg2), i)
