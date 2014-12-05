'''
Created on Jul 2, 2011

@author: mplajner
'''

from xml.dom import minidom
import logging
from cPickle import load, dump
from hashlib import md5 # pylint: disable=E0611

class XMLFile(object):
    '''Takes care of XML file operations such as reading and writing.'''

    def __init__(self):
        self.xmlResult = '<?xml version="1.0" encoding="UTF-8"?><env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">\n'
        self.declaredVars = []
        self.log = logging.getLogger('XMLFile')

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

                elif action == 'search_path':
                    if node.childNodes:
                        value = str(node.childNodes[0].data)
                    else:
                        value = ''
                    variables.append((action, (value, None, None)))

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
