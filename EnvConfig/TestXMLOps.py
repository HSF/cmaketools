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
        self.operations = xmlModule.XMLOperations()


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

    def testCheck(self):
        '''Test if the XML file check works'''
        self.control = Control.Environment(useAsWriter = True)
        self.control.append('myVar', 'app1:app2')
        self.control.prepend('myVar', 'app1:pre2')
        self.control.unset('myVar')
        self.control.set('myVar', 'set1:app2')

        self.control.finishXMLinput('testOutputFile.xml')
        self.operations.check('testOutputFile.xml')

        self.assertEqual(self.operations.report.error(0)[1], 'myVar')
        self.assertEqual(self.operations.report.error(0)[2], 'unset overwrite')
        self.assertEqual(self.operations.report.error(1)[1], 'myVar')
        self.assertEqual(self.operations.report.error(1)[2], 'set overwrite')

        os.remove('testOutputFile.xml')

    def testMerge(self):
        self.control = Control.Environment(useAsWriter = True)


        self.control.set('MY_PATH','delVal')
        self.control.unset('MY_PATH')

        self.control.set('MY_PATH','setVal:multVal')
        self.control.append('MY_PATH','appVal:multVal2')
        self.control.prepend('MY_PATH','prepVal')

        self.control.finishXMLinput('testOutputFile.xml')

        self.control.startXMLinput()
        self.control.append('MY_PATH','appVal2')
        self.control.prepend('MY_PATH','prepVal2:multVal:multVal2')
        self.control.remove('MY_PATH','multVal2')
        self.control.finishXMLinput('testOutputFile2.xml')

        self.operations.merge('testOutputFile.xml', 'testOutputFile2.xml', 'testOutputFile.xml')

        self.control = Control.Environment()
        self.control.loadXML('testOutputFile.xml')

        self.assertFalse('delVal' in self.control['MY_PATH'])

        self.assertTrue('appVal' in self.control['MY_PATH'])
        self.assertTrue('appVal2' in self.control['MY_PATH'])
        self.assertTrue('prepVal' in self.control['MY_PATH'])
        self.assertTrue('prepVal' in self.control['MY_PATH'])
        self.assertTrue('prepVal2' in self.control['MY_PATH'])
        self.assertTrue('multVal' in self.control['MY_PATH'])
        self.assertTrue('setVal' in self.control['MY_PATH'])

        self.assertFalse('multVal2' in self.control['MY_PATH'])

        os.remove('testOutputFile.xml')
        os.remove('testOutputFile2.xml')

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
