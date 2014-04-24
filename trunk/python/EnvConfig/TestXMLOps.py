'''
Created on Jul 15, 2011

@author: mplajner
'''
import unittest
import os
from StringIO import StringIO

from EnvConfig import Control
from EnvConfig import xmlModule

class Test(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFileLoad(self):
        '''Test loading of previously written file.'''
        self.control = Control.Environment(useAsWriter = True)
        self.control.unset('varToUnset')

        self.control.declare('myVar', 'list', True)
        self.control.set('myVar', 'setVal:$local')
        self.control.append('myVar', 'appVal:appVal2')
        self.control.prepend('myVar', 'prepVal:prepVal2')

        self.control.declare('myScalar', 'scalar', False)
        self.control.set('myScalar', 'setValscal')
        self.control.append('myScalar', 'appValscal')
        self.control.prepend('myScalar', 'prepValscal')

        self.control.declare('myScalar2', 'scalar', True)

        self.control.finishXMLinput('testOutputFile.xml')

        loader = xmlModule.XMLFile()
        variables = loader.variable('testOutputFile.xml')

        expected = [('declare', ('varToUnset', 'list', 'false')),
                    ('unset', ('varToUnset', '', None)),
                    ('declare', ('myVar', 'list', 'true')),
                    ('set', ('myVar', 'setVal:$local', None)),
                    ('append', ('myVar', 'appVal:appVal2', None)),
                    ('prepend', ('myVar', 'prepVal:prepVal2', None)),
                    ('declare', ('myScalar', 'scalar', 'false')),
                    ('set', ('myScalar', 'setValscal', None)),
                    ('append', ('myScalar', 'appValscal', None)),
                    ('prepend', ('myScalar', 'prepValscal', None)),
                    ('declare', ('myScalar2', 'scalar', 'true'))]

        self.assertEqual(variables, expected)

        os.remove('testOutputFile.xml')

    def testParsing(self):
        data = StringIO('''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:declare local="false" type="list" variable="varToUnset"/>
<env:unset variable="varToUnset"/>
<env:declare local="true" type="list" variable="myVar"/>
<env:set variable="myVar">setVal:$local</env:set>
<env:append variable="myVar">appVal:appVal2</env:append>
<env:prepend variable="myVar">prepVal:prepVal2</env:prepend>
<env:declare local="false" type="scalar" variable="myScalar"/>
<env:set variable="myScalar">setValscal</env:set>
<env:append variable="myScalar">appValscal</env:append>
<env:prepend variable="myScalar">prepValscal</env:prepend>
<env:declare local="true" type="scalar" variable="myScalar2"/>
<env:include>some_file.xml</env:include>
<env:include hints="some:place">another_file.xml</env:include>
</env:config>''')

        loader = xmlModule.XMLFile()
        variables = loader.variable(data)

        expected = [('declare', ('varToUnset', 'list', 'false')),
                    ('unset', ('varToUnset', '', None)),
                    ('declare', ('myVar', 'list', 'true')),
                    ('set', ('myVar', 'setVal:$local', None)),
                    ('append', ('myVar', 'appVal:appVal2', None)),
                    ('prepend', ('myVar', 'prepVal:prepVal2', None)),
                    ('declare', ('myScalar', 'scalar', 'false')),
                    ('set', ('myScalar', 'setValscal', None)),
                    ('append', ('myScalar', 'appValscal', None)),
                    ('prepend', ('myScalar', 'prepValscal', None)),
                    ('declare', ('myScalar2', 'scalar', 'true')),
                    ('include', ('some_file.xml', None, '')),
                    ('include', ('another_file.xml', None, 'some:place'))]

        self.assertEqual(variables, expected)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
