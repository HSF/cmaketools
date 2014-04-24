'''
Created on Jul 12, 2011

@author: mplajner
'''
import unittest
import os
import shutil
from tempfile import mkdtemp

from EnvConfig import Variable
from EnvConfig import Control

# Keep only some Variable processors.
saved_processors = Variable.processors
Variable.processors = [Variable.EnvExpander,
                       Variable.PathNormalizer,
                       Variable.DuplicatesRemover]

def buildDir(files, rootdir=os.curdir):
    '''
    Create a directory structure from the content of files.

    @param files: a dictionary or list of pairs mapping a filename to the content
                  if the content is a dictionary, recurse
    @param rootdir: base directory
    '''
    if type(files) is dict:
        files = files.items()

    # ensure that the root exists (to allow empty directories)
    if not os.path.exists(rootdir):
        os.makedirs(rootdir)

    # create all the entries
    for filename, data in files:
        filename = os.path.join(rootdir, filename)
        if type(data) is dict:
            buildDir(data, filename)
        else:
            d = os.path.dirname(filename)
            if not os.path.exists(d):
                os.makedirs(d)
            f = open(filename, "w")
            if data:
                f.write(data)
            f.close()

class TempDir(object):
    '''
    Class for easy creation, use and removal of temporary directory structures.
    '''
    def __init__(self, files=None):
        self.tmpdir = mkdtemp()
        if files is None:
            files = {}
        buildDir(files, self.tmpdir)

    def __del__(self):
        shutil.rmtree(self.tmpdir, ignore_errors=False)

    def __call__(self, *args):
        '''
        Return the absolute path to a file in the temporary directory.
        '''
        return os.path.join(self.tmpdir, *args)

class Test(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass


    def testValues(self):
        '''Test of value appending, prepending, setting, unsetting, removing'''
        control = Control.Environment()

        self.assertFalse('MY_PATH' in control.vars())
        control.append('MY_PATH', 'newValue')
        self.assertTrue('MY_PATH' in control.vars())
        var = control.var('MY_PATH')

        control.append('MY_PATH', 'newValue:secondVal:valval')
        self.assertTrue(var[len(var)-1] == 'valval')

        self.assertTrue('newValue' in var)
        control.remove('MY_PATH', 'newValue')
        self.assertFalse('newValue' in var)

        control.prepend('MY_PATH', 'newValue')
        self.assertTrue('newValue' == var[0])

        control.set('MY_PATH', 'hi:hello')
        self.assertTrue(len(var) == 2)
        self.assertTrue('hi' == var[0])

        control.unset('MY_PATH')
        self.assertTrue('MY_PATH' not in control)


    def testWrite(self):
        """XML file write and load test"""
        control = Control.Environment(useAsWriter = True)
        control.unset('MY_PATH')
        control.set('MY_PATH', 'set:toDelete')
        control.append('MY_PATH', 'appended:toDelete')
        control.prepend('MY_PATH', 'prepended:toDelete')
        control.remove('MY_PATH', 'toDelete')
        control.finishXMLinput('testOutputFile.xml')

        control = Control.Environment()
        self.assertFalse('MY_PATH' in control.vars())
        control.loadXML('testOutputFile.xml')

        self.assertTrue('MY_PATH' in control.vars())
        var = control.var('MY_PATH')
        self.assertTrue(var[0] == 'prepended')
        self.assertTrue(var[1] == 'set')
        self.assertTrue(var[2] == 'appended')
        self.assertFalse('toDelete' in var)

        os.remove('testOutputFile.xml')


    def testWriteWithList(self):
        """XML file write and load test"""
        control = Control.Environment(useAsWriter = True)
        control.unset('MY_PATH')
        control.set('MY_PATH', ['set','toDelete'])
        control.append('MY_PATH', ['appended','toDelete'])
        control.prepend('MY_PATH', ['prepended','toDelete'])
        control.remove('MY_PATH', ['toDelete'])
        control.finishXMLinput('testOutputFile.xml')

        control = Control.Environment()
        self.assertFalse('MY_PATH' in control.vars())
        control.loadXML('testOutputFile.xml')

        self.assertTrue('MY_PATH' in control.vars())
        var = control.var('MY_PATH')
        self.assertTrue(var[0] == 'prepended')
        self.assertTrue(var[1] == 'set')
        self.assertTrue(var[2] == 'appended')
        self.assertFalse('toDelete' in var)

        os.remove('testOutputFile.xml')


    def testSaveToXML(self):
        """XML file write and load test"""
        control = Control.Environment()

        control.unset('MY_PATH')
        control.set('MY_PATH', 'set:toDelete')
        control.append('MY_PATH', 'appended:toDelete')
        control.prepend('MY_PATH', 'prepended:toDelete')
        control.remove('MY_PATH', 'toDelete')
        control.writeToXMLFile('testOutputFile.xml')

        control = Control.Environment()
        self.assertFalse('MY_PATH' in control.vars())
        control.loadXML('testOutputFile.xml')

        self.assertTrue('MY_PATH' in control.vars())
        var = control.var('MY_PATH')
        self.assertTrue(var[0] == 'prepended')
        self.assertTrue(var[1] == 'set')
        self.assertTrue(var[2] == 'appended')
        self.assertFalse('toDelete' in var)

        os.remove('testOutputFile.xml')

    def testSaveToFile(self):
        '''Test addition of variable to system'''
        control = Control.Environment()

        control.append('sysVar', 'newValue:lala')
        control.writeToFile('setupFile.txt')

        with open('setupFile.txt', "r") as f:
            f.readline()
            stri = f.readline()
        f.close()

        self.assertEqual(stri, 'export sysVar=newValue:lala\n')

        os.remove('setupFile.txt')

    def testSearch(self):
        '''Testing searching in variables'''
        control = Control.Environment()

        control.append('MY_PATH', 'newValue:mess:something new:aaaabbcc')

        def count(val, regExp = False):
            return len(control.search('MY_PATH', val, regExp))

        self.assertEqual(count('new'), 0)
        self.assertEqual(count('newValue'), 1)

        self.assertEqual(count('me', False), 0)
        self.assertEqual(count('me', True), 2)

        self.assertEqual(count('cc', False), 0)
        self.assertEqual(count('cc', True), 1)

        self.assertEqual(count('a{2}b{2}c{2}', True), 1)
        self.assertEqual(count('a{2}b{2}', True), 1)
        self.assertEqual(count('a{1}b{2}c{2}', True), 1)
        self.assertEqual(count('a{1}b{1}c{2}', True), 0)
        self.assertEqual(count('a{1,2}b{1,2}c{2}', True), 1)
        self.assertEqual(count('a{2,3}', True), 1)
        self.assertEqual(count('a{2,3}?', True), 1)

    def testVariables(self):
        '''Tests variables creation and redeclaration.'''
        control = Control.Environment()

        control.append('MY_PATH', 'newValue')
        self.assertFalse(control.var('MY_PATH').local)
        self.assertTrue(isinstance(control.var('MY_PATH'),Variable.List))

        control.declare('loc', 'list', True)
        self.assertTrue(control.var('loc').local)
        self.assertTrue(isinstance(control.var('loc'),Variable.List))

        control.declare('myVar2', 'scalar', False)
        self.assertFalse(control.var('myVar2').local)
        self.assertTrue(isinstance(control.var('myVar2'),Variable.Scalar))

        control.declare('loc2', 'scalar', True)
        self.assertTrue(control.var('loc2').local)
        self.assertTrue(isinstance(control.var('loc2'),Variable.Scalar))

        control.declare('MY_PATH', 'list', False)
        self.failUnlessRaises(Variable.EnvError, control.declare, 'MY_PATH', 'list', True)
        self.failUnlessRaises(Variable.EnvError, control.declare, 'MY_PATH', 'scalar', True)
        self.failUnlessRaises(Variable.EnvError, control.declare, 'MY_PATH', 'scalar', True)

        control.declare('loc', 'list', True)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc', 'list', False)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc', 'scalar', True)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc', 'scalar', True)

        control.declare('myVar2', 'scalar', False)
        self.failUnlessRaises(Variable.EnvError, control.declare,'myVar2', 'list', False)
        self.failUnlessRaises(Variable.EnvError, control.declare,'myVar2', 'list', True)
        self.failUnlessRaises(Variable.EnvError, control.declare,'myVar2', 'scalar', True)

        control.declare('loc2', 'scalar', True)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc2', 'list', False)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc2', 'list', True)
        self.failUnlessRaises(Variable.EnvError, control.declare,'loc2', 'scalar', False)


    def testDelete(self):
        control = Control.Environment()

        control.append('MY_PATH','myVal:anotherVal:lastVal')
        control.remove('MY_PATH','anotherVal')

        self.assertFalse('anotherVal' in control['MY_PATH'])
        self.assertTrue('myVal' in control['MY_PATH'])
        self.assertTrue('lastVal' in control['MY_PATH'])

        control.set('MY_PATH','myVal:anotherVal:lastVal:else')
        control.remove('MY_PATH', '^anotherVal$', False)
        self.assertTrue('anotherVal' in control['MY_PATH'])
        control.remove('MY_PATH', '^anotherVal$', True)
        self.assertFalse('anotherVal' in control['MY_PATH'])
        self.assertTrue('myVal' in control['MY_PATH'])
        self.assertTrue('lastVal' in control['MY_PATH'])
        self.assertTrue('lastVal' in control['MY_PATH'])
        control.remove('MY_PATH', 'Val', True)
        self.assertTrue('else' in control['MY_PATH'])
        self.assertTrue(len(control['MY_PATH']) == 1)


        control.declare('myLoc', 'scalar', False)
        control.append('myLoc','myVal:anotherVal:lastVal')
        control.remove('myLoc', 'Val:', True)
        self.assertTrue(str(control['myLoc']) == 'myanotherlastVal')


    def testSystemEnvironment(self):
        control = Control.Environment()

        os.environ['MY_PATH'] = '$myVal'
        os.environ['myScal'] = '$myVal'

        control.set('ABC','anyValue')
        control.declare('MY_PATH', 'list', False)
        control.append('MY_PATH','$ABC')
        self.assertTrue(control['MY_PATH'].value(True) == '$myVal:anyValue')

        control.declare('myScal', 'scalar', False)
        control.append('myScal', '$ABC')
        self.assertTrue(control['myScal'].value(True) == '$myValanyValue')


    def testDependencies(self):
        control = Control.Environment()

        control.declare('myVar', 'list', False)

        control.declare('loc', 'list', True)
        control.append('loc','locVal')
        control.append('loc','locVal2')

        control.declare('scal', 'scalar', False)
        control.append('scal','scalVal')
        control.append('scal','scalVal2')

        control.declare('scal2', 'scalar', True)
        control.append('scal2','locScal')
        control.append('scal2','locScal2')

        control.set('myVar', 'newValue:$loc:endValue')
        self.assertEqual(str(control['myVar']),'newValue:locVal:locVal2:endValue')

        control.set('myVar', 'newValue:$scal:endValue')
        self.assertEqual(str(control['myVar']),'newValue:scalValscalVal2:endValue')

        control.set('myVar', 'new${scal}Value:endValue')
        self.assertEqual(str(control['myVar']),'newscalValscalVal2Value:endValue')

        control.set('myVar', 'bla:$myVar:Value')
        self.assertEqual(str(control['myVar']),'bla:newscalValscalVal2Value:endValue:Value')

        control.set('scal', 'new${scal2}Value')
        self.assertEqual(str(control['scal']),'newlocScallocScal2Value')

        control.set('scal', 'new${loc}Value')
        self.assertEqual(str(control['scal']),'newlocVal:locVal2Value')

        control.set('scal2', 'new${scal2}Value')
        self.assertEqual(str(control['scal2']),'newlocScallocScal2Value')

    def testInclude(self):
        tmp = TempDir({'first.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="main">first</env:set>
<env:append variable="test_path">data1</env:append>
<env:include>first_inc.xml</env:include>
</env:config>''',
                       'second.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="main">second</env:set>
<env:include>second_inc.xml</env:include>
<env:append variable="test_path">data1</env:append>
</env:config>''',
                       'third.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="main">third</env:set>
<env:append variable="test_path">data1</env:append>
<env:include>subdir/first_inc.xml</env:include>
</env:config>''',
                       'fourth.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="main">fourth</env:set>
<env:include hints="subdir2">fourth_inc.xml</env:include>
</env:config>''',
                       'recursion.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="main">recursion</env:set>
<env:include>recursion.xml</env:include>
</env:config>''',
                       'first_inc.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:append variable="test_path">data2</env:append>
<env:append variable="derived">another_${main}</env:append>
</env:config>''',
                       'subdir': {'second_inc.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:append variable="test_path">data0</env:append>
<env:set variable="map">this_is_second_inc</env:set>
</env:config>''',
                                  'first_inc.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:append variable="derived">second_${main}</env:append>
</env:config>''',
                                  'fourth_inc.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:append variable="included">from subdir</env:append>
</env:config>''',},
                       'subdir2': {'fourth_inc.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:append variable="included">from subdir2</env:append>
</env:config>''',}})

        if 'ENVXMLPATH' in os.environ:
            del os.environ['ENVXMLPATH']
        control = Control.Environment(searchPath=[])

        #self.assertRaises(OSError, control.loadXML, tmp('first.xml'))
        control.loadXML(tmp('first.xml'))
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        control = Control.Environment(searchPath=[tmp()])
        control.loadXML(tmp('first.xml'))
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        control = Control.Environment(searchPath=[tmp()])
        control.loadXML('first.xml')
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        control = Control.Environment(searchPath=[tmp()])
        self.assertRaises(OSError, control.loadXML, tmp('second.xml'))

        control = Control.Environment(searchPath=[tmp(), tmp('subdir')])
        control.loadXML(tmp('second.xml'))
        self.assertEqual(str(control['main']), 'second')
        self.assertEqual(str(control['test_path']), 'data0:data1')
        self.assertEqual(str(control['map']), 'this_is_second_inc')

        control = Control.Environment(searchPath=[tmp(), tmp('subdir')])
        control.loadXML(tmp('first.xml'))
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        control = Control.Environment(searchPath=[tmp('subdir'), tmp()])
        control.loadXML(tmp('first.xml'))
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        control = Control.Environment(searchPath=[tmp('subdir'), tmp()])
        control.loadXML('first.xml')
        self.assertEqual(str(control['main']), 'first')
        self.assertEqual(str(control['test_path']), 'data1:data2')
        self.assertEqual(str(control['derived']), 'another_first')

        os.environ['ENVXMLPATH'] = os.pathsep.join([tmp(), tmp('subdir')])
        control = Control.Environment(searchPath=[])
        control.loadXML(tmp('second.xml'))
        self.assertEqual(str(control['main']), 'second')
        self.assertEqual(str(control['test_path']), 'data0:data1')
        self.assertEqual(str(control['map']), 'this_is_second_inc')
        del os.environ['ENVXMLPATH']

        control = Control.Environment(searchPath=[])
        control.loadXML(tmp('third.xml'))
        self.assertEqual(str(control['main']), 'third')
        self.assertEqual(str(control['test_path']), 'data1')
        self.assertEqual(str(control['derived']), 'second_third')

        control = Control.Environment(searchPath=[tmp('subdir')])
        control.loadXML(tmp('fourth.xml'))
        self.assertEqual(str(control['main']), 'fourth')
        self.assertEqual(str(control['included']), 'from subdir')

        control = Control.Environment(searchPath=[])
        control.loadXML(tmp('fourth.xml'))
        self.assertEqual(str(control['main']), 'fourth')
        self.assertEqual(str(control['included']), 'from subdir2')

        control = Control.Environment(searchPath=[])
        #self.assertRaises(OSError, control.loadXML, tmp('first.xml'))
        control.loadXML(tmp('recursion.xml'))


    def testFileDir(self):
        tmp = TempDir({'env.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:set variable="mydirs">${.}</env:set>
<env:set variable="myparent">${.}/..</env:set>
</env:config>'''})

        control = Control.Environment()
        control.loadXML(tmp('env.xml'))
        self.assertEqual(str(control['mydirs']), tmp())
        self.assertEqual(str(control['myparent']), os.path.dirname(tmp()))

        olddir = os.getcwd()
        os.chdir(tmp())
        try:
            control = Control.Environment()
            control.loadXML('env.xml')
            self.assertEqual(str(control['mydirs']), tmp())
            self.assertEqual(str(control['myparent']), os.path.dirname(tmp()))
        finally:
            os.chdir(olddir)

    def testDefaults(self):
        tmp = TempDir({'env.xml':
'''<?xml version="1.0" ?>
<env:config xmlns:env="EnvSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="EnvSchema ./EnvSchema.xsd ">
<env:default variable="var1">value1</env:default>
<env:declare variable="var2" local="true" />
<env:default variable="var2">test2</env:default>
</env:config>'''})

        if 'var1' in os.environ:
            del os.environ['var1']
        control = Control.Environment()
        control.loadXML(tmp('env.xml'))
        self.assertEqual(str(control['var1']), "value1")
        self.assertEqual(str(control['var2']), "test2")

        os.environ['var1'] = "some_value"
        control = Control.Environment()
        control.loadXML(tmp('env.xml'))
        self.assertEqual(str(control['var1']), "some_value")
        self.assertEqual(str(control['var2']), "test2")


    def testVariableManipulations(self):
        l = Variable.List('PATH')

        l.set("/usr/bin:/some//strange/../nice/./location")
        assert l.value(asString=True) == "/usr/bin:/some/nice/location"

        l.append("/another/path")
        assert l.value(asString=True) == "/usr/bin:/some/nice/location:/another/path"

        # duplicates removal
        l.append("/usr/bin")
        assert l.value(asString=True) == "/usr/bin:/some/nice/location:/another/path"
        l.prepend("/another/path")
        assert l.value(asString=True) == "/another/path:/usr/bin:/some/nice/location"

        s = Variable.Scalar('VAR')

        s.set("/usr/bin")
        assert s.value(asString=True) == "/usr/bin"

        s.set("/some//strange/../nice/./location")
        assert s.value(asString=True) == "/some/nice/location"

        # This is undefined
        # l.set("http://cern.ch")

        s.set("http://cern.ch")
        assert s.value(asString=True) == "http://cern.ch"

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()