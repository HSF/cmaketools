from tempfile import mkdtemp
import shutil
import os
import re

# use a private cache for the tests
os.environ['CMT2CMAKECACHE'] = 'test.cache'
if os.path.exists('test.cache'):
    os.remove('test.cache')

import cmt2cmake
cmt2cmake.open_cache()

# prepare the cache for the tests
cmt2cmake.cache['GaudiKernel'] = {'libraries': ['GaudiKernel'],
                                  'includes': False}
cmt2cmake.cache['GaudiUtils'] = {'libraries': ['GaudiUtilsLib'],
                                 'includes': False}
cmt2cmake.cache['LHCbKernel'] = {'libraries': ['LHCbKernel'],
                                 'includes': False}
cmt2cmake.cache['SomeSubdir'] = {'libraries': ['SubdirLib'],
                                 'includes': False}
cmt2cmake.cache['JustHeaders'] = {'libraries': [],
                                  'includes': True}
cmt2cmake.cache[repr(('Baseproject', 'v1r0'))] = {'heptools': '65'}
cmt2cmake.cache[repr(('TestProjectHT', 'v3r0'))] = {'heptools': '23'}


cmt2cmake.data_packages = set(['DataPack', 'Another/DtPkg', 'SpecialThing'])

#
# Helpers
#

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

class PackWrap(cmt2cmake.Package):
    """
    Helper class to test the Package.
    """
    def __init__(self, name, requirements, files=None):
        if not files:
            files = {}
        files["cmt/requirements"] = requirements

        self.tmpdir = mkdtemp()
        rootdir = os.path.join(self.tmpdir, name)
        buildDir(files, rootdir)

        super(PackWrap, self).__init__(rootdir)

    def __del__(self):
        shutil.rmtree(self.tmpdir, ignore_errors=False)

class ProjWrap(cmt2cmake.Project):
    """
    Helper class to test the Project.
    """
    def __init__(self, name, proj_cmt, files=None):
        if not files:
            files = {}
        files["cmt/project.cmt"] = proj_cmt

        self.tmpdir = mkdtemp()
        rootdir = os.path.join(self.tmpdir, name)
        buildDir(files, rootdir)

        super(ProjWrap, self).__init__(rootdir)

    def __del__(self):
        shutil.rmtree(self.tmpdir, ignore_errors=False)


def getCalls(function, cmakelists):
    '''
    extracts the arguments to all the calls to a cmake function
    '''
    exp = re.compile(r'\b{0}\s*\(([^)]*)\)'.format(function), flags=re.MULTILINE)
    return [m.group(1) for m in exp.finditer(cmakelists)]

#
# Tests
#

def test_not_a_package():
    d = mkdtemp()
    buildDir({'NoPackage': {'a_file.txt': None}}, d)
    try:
        cmt2cmake.Package(os.path.join(d, 'NoPackage'))
        assert False, 'bad package not recognized'
    except ValueError:
        pass
    finally:
        shutil.rmtree(d)


def test_pack_header():
    requirements = """
    package ThisIsAPackage
    version v123r456

    branches   cmt branches are ignored
    macro test parsing of \\
          multi line
    """
    pkg = PackWrap("ThisIsAPackage", requirements)

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_subdir", cmakelists)
    assert calls, "gaudi_subdir not called"
    assert len(calls) == 1, "gaudi_subdir called more than once"

    args = calls[0].strip().split()
    assert args == ["ThisIsAPackage", "v123r456"], args

def test_pack_deps():
    requirements = """
    package Test
    version v1r0

    # series of uses
    use GaudiKernel v*
    use GaudiAlg *
    use GaudiPolicy *
    use GaudiCoreSvc v* # comment
    use GaudiUtils * -no_auto_imports

    use LHCbKernel v* Kernel
    """
    pkg = PackWrap("Test", requirements)

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_depends_on_subdirs", cmakelists)
    assert calls, "gaudi_depends_on_subdirs not called"

    args = set()
    for call in calls:
        args.update(call.strip().split())
    expected = set(['GaudiKernel', 'GaudiAlg', 'GaudiCoreSvc',
                    'GaudiUtils', 'Kernel/LHCbKernel'])
    assert args == expected

def test_pack_no_deps():
    requirements = """
    package Test
    version v1r0

    # no uses
    """
    pkg = PackWrap("Test", requirements)

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_depends_on_subdirs", cmakelists)
    assert not calls, "gaudi_depends_on_subdirs called"

def test_pack_ext_deps():
    requirements = """
    package Test
    version v1r0

    # series of uses
    use Boost v* LCG_Interfaces
    use Python v* LCG_Interfaces
    use XercesC v* LCG_Interfaces -no_auto_imports
    """
    pkg = PackWrap("Test", requirements)

    cmakelists = pkg.generate()
    print cmakelists

    expected = set(['Boost', 'XercesC'])

    calls = getCalls("find_package", cmakelists)
    assert calls, "find_pacakge not called"
    assert len(calls) == len(expected)

    args = set()
    for call in calls:
        args.add(call.strip().split()[0])
    print args
    assert args == expected

def test_install_headers():
    requirements = '''
#============================================================================
package           Tell1Kernel
version           v1r12p1

# Structure, i.e. directories to process.
#============================================================================
branches          cmt doc Tell1Kernel

# Used packages
#============================================================================
use GaudiPolicy      v*

apply_pattern install_more_includes more=Tell1Kernel
    '''
    pkg = PackWrap("Tell1Kernel", requirements, files={"Tell1Kernel/hdr.h": None})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_install_headers", cmakelists)
    assert calls

    args = set()
    for call in calls:
        args.update(call.strip().split())
    expected = set(['Tell1Kernel'])
    assert args == expected

def test_install_python():
    requirements = '''
package Test
version v1r0

apply_pattern install_python_modules
    '''
    pkg = PackWrap("Test", requirements, files={"python/Test/__init__.py": None})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_install_python_modules", cmakelists)
    assert calls

def test_install_python2():
    requirements = '''
package Test
version v1r0

macro TestConfUserModules "Test.CustomModule1 Test.CustomModule2"

apply_pattern install_python_modules
    '''
    pkg = PackWrap("Test", requirements, files={"python/Test/__init__.py": None})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_install_python_modules", cmakelists)
    assert calls

    calls = getCalls("set_property", cmakelists)
    assert calls
    args = calls[0].strip().split()
    assert args == ['DIRECTORY', 'PROPERTY', 'CONFIGURABLE_USER_MODULES', 'Test.CustomModule1', 'Test.CustomModule2'], args

def test_install_scripts():
    requirements = '''
package Test
version v1r0

apply_pattern install_scripts
    '''
    pkg = PackWrap("Test", requirements, files={"scripts/someScript": None})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_install_scripts", cmakelists)
    assert calls

def test_qmtest():
    requirements = '''
package Test
version v1r0

apply_pattern QMTest
    '''
    pkg = PackWrap("Test", requirements, files={"tests/qmtest/test.qms/a_test.qmt": None})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_test", cmakelists)
    assert calls, "no test added"
    assert len(calls) == 1, "gaudi_add_test called more than once"

    args = calls[0].strip().split()
    assert args == ["QMTest", "QMTEST"]

def test_libraries():
    requirements = '''
package Test
version v1r0

library TestLib lib/*.cpp
apply_pattern linker_library library=TestLib

library TestComp component/*.cpp
apply_pattern component_library library=TestComp

library TestTestLib test/lib/*.cpp -group=tests
apply_pattern linker_library library=TestTestLib

library TestTestComp test/component/*.cpp -group=tests
apply_pattern component_library library=TestTestComp

apply_pattern install_more_includes more=TestIncludes
    '''
    pkg = PackWrap("Test", requirements, files={'TestIncludes': {}})

    print 'components', pkg.component_libraries
    print 'linker', pkg.linker_libraries
    print 'libraries', pkg.libraries

    assert pkg.component_libraries == set(['TestComp', 'TestTestComp'])
    assert pkg.linker_libraries == set(['TestLib', 'TestTestLib'])
    assert pkg.libraries

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_library", cmakelists)
    assert len(calls) == 2, "gaudi_add_library wrong count %d" % len(calls)
    l = calls[0]
    assert re.match(r' *TestLib\b', l)
    assert re.search(r'\bPUBLIC_HEADERS +TestIncludes', l)
    l = calls[1]
    assert re.match(r' *TestTestLib\b', l)
    assert re.search(r'\bPUBLIC_HEADERS +TestIncludes', l)
    assert re.search(r'\bLINK_LIBRARIES +TestLib', l)

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 2, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0]
    assert re.match(r' *TestComp\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS\b', l)
    assert re.search(r'\bLINK_LIBRARIES +TestLib', l)
    l = calls[1]
    assert re.match(r' *TestTestComp\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS', l)
    assert re.search(r'\bLINK_LIBRARIES +TestLib +TestTestLib', l)

def test_libraries_2():
    requirements = '''
package Test
version v1r0

use Boost v* LCG_Interfaces
use XercesC v* LCG_Interfaces -no_auto_imports

library Lib1 lib1/*.cpp
apply_pattern component_library library=Lib1

library Lib2 lib2/*.cpp -import=XercesC
apply_pattern component_library library=Lib2

# We do not use variables
library Lib3 lib3/*.cpp a_variable=some_value
apply_pattern component_library library=Lib3
    '''
    pkg = PackWrap("Test", requirements, files={})

    print 'components', pkg.component_libraries
    print 'libraries', pkg.libraries

    assert pkg.component_libraries == set(['Lib1', 'Lib2', 'Lib3'])
    assert pkg.libraries

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 3, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0]
    assert re.match(r' *Lib1\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS\b', l)
    assert re.search(r'\bLINK_LIBRARIES +Boost', l)
    assert re.search(r'\bINCLUDE_DIRS +Boost', l)
    l = calls[1]
    assert re.match(r' *Lib2\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS', l)
    assert re.search(r'\bLINK_LIBRARIES +Boost +XercesC', l)
    assert re.search(r'\bINCLUDE_DIRS +Boost +XercesC', l)
    l = calls[2]
    assert re.match(r' *Lib3\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS', l)
    assert re.search(r'\bLINK_LIBRARIES +Boost', l)
    assert re.search(r'\bINCLUDE_DIRS +Boost', l)

def test_libraries_3():
    # some corner cases
    # FIXME: we should actually test the warning messages
    requirements = '''
package Test
version v1r0

library Lib1
apply_pattern component_library library=Lib1

library Lib2 lib2/*.cpp
apply_pattern linker_library library=Lib2

library Lib3 lib3/*.cpp

library Lib4  lib4/*.cpp
apply_pattern linker_library library="Lib4"

    '''
    pkg = PackWrap("Test", requirements, files={})

    print 'components', pkg.component_libraries
    print 'linker', pkg.linker_libraries
    print 'libraries', pkg.libraries

    assert pkg.component_libraries == set(['Lib1'])
    assert pkg.linker_libraries == set(['Lib2', 'Lib4'])
    assert len(pkg.libraries) == 4

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 1, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0]
    assert re.match(r' *Lib1\b', l)
    assert not re.search(r'\bPUBLIC_HEADERS\b', l)

    calls = getCalls("gaudi_add_library", cmakelists)
    assert len(calls) == 3, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0]
    assert re.match(r' *Lib2\b', l)
    assert re.search(r'\bNO_PUBLIC_HEADERS', l)

    l = calls[1]
    assert re.match(r' *Lib3\b', l)
    assert re.search(r'\bNO_PUBLIC_HEADERS', l)

    l = calls[2]
    assert re.match(r' *Lib4\b', l)
    assert re.search(r'\bNO_PUBLIC_HEADERS', l)

def test_libraries_fix_src_path():
    requirements = '''
package Test
version v1r0

library TestLib1 ../src/subdir/*.cpp
apply_pattern linker_library library=TestLib1

library TestLib2 ../tests/src/subdir/*.cpp
apply_pattern linker_library library=TestLib2

library TestLib3 subdir/*.cpp
apply_pattern linker_library library=TestLib3
    '''
    pkg = PackWrap("Test", requirements, files={'TestIncludes': {}})

    assert pkg.linker_libraries == set(['TestLib1', 'TestLib2', 'TestLib3'])

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_library", cmakelists)
    assert len(calls) == 3, "gaudi_add_library wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'TestLib1'
    assert l[1] == 'src/subdir/*.cpp'

    l = calls[1].strip().split()
    assert l[0] == 'TestLib2'
    assert l[1] == 'tests/src/subdir/*.cpp'

    l = calls[2].strip().split()
    assert l[0] == 'TestLib3'
    assert l[1] == 'src/subdir/*.cpp'

def test_subdir_links():
    requirements = '''
package Test
version v1r0

use Boost v* LCG_Interfaces
use XercesC v* LCG_Interfaces -no_auto_imports

use GaudiKernel *
use GaudiUtils * -no_auto_imports


library Lib1 *.cpp
apply_pattern component_library library=Lib1

library Lib2 *.cpp -import=XercesC
apply_pattern component_library library=Lib2

library Lib3 *.cpp -import=GaudiUtils
apply_pattern component_library library=Lib3
    '''
    pkg = PackWrap("Test", requirements, files={})

    print 'components', pkg.component_libraries
    print 'linker', pkg.linker_libraries
    print 'libraries', pkg.libraries

    assert pkg.component_libraries == set(['Lib1', 'Lib2', 'Lib3'])
    assert len(pkg.libraries) == 3

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 3, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Lib1'
    links = set(l[l.index('LINK_LIBRARIES')+1:])
    assert links == set(['Boost', 'GaudiKernel'])

    l = calls[1].strip().split()
    assert l[0] == 'Lib2'
    assert 'LINK_LIBRARIES' in l
    links = set(l[l.index('LINK_LIBRARIES')+1:])
    assert links == set(['Boost', 'GaudiKernel', 'XercesC'])

    l = calls[2].strip().split()
    assert l[0] == 'Lib3'
    assert 'LINK_LIBRARIES' in l
    links = set(l[l.index('LINK_LIBRARIES')+1:])
    assert links == set(['Boost', 'GaudiKernel', 'GaudiUtilsLib'])

def test_subdir_links_hat():
    requirements = '''
package Test
version v1r0

use LHCbKernel * Kernel
use SomeSubdir * Hat -no_auto_imports

library Lib1 *.cpp
apply_pattern component_library library=Lib1

library Lib2 *.cpp -import=SomeSubdir
apply_pattern component_library library=Lib2
    '''
    pkg = PackWrap("Test", requirements, files={})

    print 'components', pkg.component_libraries
    print 'linker', pkg.linker_libraries
    print 'libraries', pkg.libraries

    assert pkg.component_libraries == set(['Lib1', 'Lib2'])
    assert len(pkg.libraries) == 2

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 2, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Lib1'
    links = set(l[l.index('LINK_LIBRARIES')+1:])
    assert links == set(['LHCbKernel'])

    l = calls[1].strip().split()
    assert l[0] == 'Lib2'
    links = set(l[l.index('LINK_LIBRARIES')+1:])
    assert links == set(['LHCbKernel', 'SubdirLib'])

def test_subdir_links_missing():
    requirements = '''
package Test
version v1r0

use UnknownSubdir *

library Lib1 *.cpp
apply_pattern component_library library=Lib1
    '''
    pkg = PackWrap("Test", requirements, files={})

    assert pkg.component_libraries == set(['Lib1'])
    assert len(pkg.libraries) == 1

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 1, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Lib1'
    assert 'LINK_LIBRARIES' not in l
    # FIXME: we should test the warning

def test_subdir_links_update():
    if 'GaudiDummy' in cmt2cmake.cache:
        del cmt2cmake.cache['GaudiDummy']

    requirements = '''
package GaudiDummy
version v1r0

apply_pattern install_more_includes more=Dummy

library Dummy *.cpp
apply_pattern linker_library library=Dummy
    '''
    PackWrap("GaudiDummy", requirements, files={'Dummy':{}})

    assert cmt2cmake.cache['GaudiDummy']['libraries'] == ['Dummy']
    assert cmt2cmake.cache['GaudiDummy']['includes'] == False

def test_subdir_headers():
    if 'GaudiDummy' in cmt2cmake.cache:
        del cmt2cmake.cache['GaudiDummy']

    requirements = '''
package GaudiDummy
version v1r0

use JustHeaders v*
use JustHeaders v* Hat

library Dummy *.cpp
apply_pattern linker_library library=Dummy
    '''
    pkg = PackWrap("GaudiDummy", requirements, files={'Dummy':{}})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_library", cmakelists)
    assert len(calls) == 1, "gaudi_add_library wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Dummy'
    assert 'INCLUDE_DIRS' in l
    links = set(l[l.index('INCLUDE_DIRS')+1:])
    assert links == set(['JustHeaders', 'Hat/JustHeaders'])

def test_subdir_headers_update():
    if 'GaudiDummy' in cmt2cmake.cache:
        del cmt2cmake.cache['GaudiDummy']

    requirements = '''
package GaudiDummy
version v1r0

apply_pattern install_more_includes more=Dummy
    '''
    PackWrap("GaudiDummy", requirements, files={'Dummy':{}})

    assert cmt2cmake.cache['GaudiDummy']['includes'] == True
    assert not cmt2cmake.cache['GaudiDummy']['libraries']

def test_write_file():
    requirements = '''
package Test
version v1r0

library Lib1 *.cpp
apply_pattern component_library library=Lib1
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    cmakefile = os.path.join(pkg.path, 'CMakeLists.txt')
    pkg.process()
    assert os.path.exists(cmakefile)
    assert open(cmakefile).read() == cmakelists

def test_write_file_exists():
    requirements = '''
package Test
version v1r0

library Lib1 *.cpp
apply_pattern component_library library=Lib1
    '''
    pkg = PackWrap("Test", requirements, files={'CMakeLists.txt': 'dummy data'})

    cmakefile = os.path.join(pkg.path, 'CMakeLists.txt')
    pkg.process()
    # FIXME: we should test the warning
    assert open(cmakefile).read() == 'dummy data'


def test_god_1():
    # some corner cases
    # FIXME: we should actually test the warning messages
    requirements = '''
package Test
version v1r0

apply_pattern god_headers files=../xml/*.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_headers", cmakelists)
    assert len(calls) == 1, "god_build_headers wrong count %d" % len(calls)

    l = calls[0].strip()
    assert l == 'xml/*.xml'

def test_god_2():
    requirements = '''
package Test
version v1r0

apply_pattern god_dictionary files=../xml/*.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_dictionary", cmakelists)
    assert len(calls) == 1, "god_build_dictionary wrong count %d" % len(calls)

    l = calls[0].strip()
    assert l == 'xml/*.xml'

def test_god_3():
    requirements = '''
package Test
version v1r0

use Boost v* LCG_Interfaces

apply_pattern god_headers files=../xml/*.xml
apply_pattern god_dictionary files=../xml/*.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_headers", cmakelists)
    assert len(calls) == 1, "god_build_headers wrong count %d" % len(calls)

    calls = getCalls("god_build_dictionary", cmakelists)
    assert len(calls) == 1, "god_build_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'xml/*.xml'
    assert 'LINK_LIBRARIES' in l
    assert l[l.index('LINK_LIBRARIES')+1] == 'Boost'
    assert 'INCLUDE_DIRS' in l
    assert l[l.index('INCLUDE_DIRS')+1] == 'Boost'

def test_god_4():
    requirements = '''
package Test
version v1r0

use Boost v* LCG_Interfaces

library Lib *.cpp
apply_pattern linker_library library=Lib

apply_pattern god_headers files=../xml/*.xml
apply_pattern god_dictionary files=../xml/*.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_headers", cmakelists)
    assert len(calls) == 1, "god_build_headers wrong count %d" % len(calls)

    calls = getCalls("gaudi_add_library", cmakelists)
    assert len(calls) == 1, "gaudi_add_library wrong count %d" % len(calls)

    calls = getCalls("god_build_dictionary", cmakelists)
    assert len(calls) == 1, "god_build_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'xml/*.xml'
    assert 'LINK_LIBRARIES' in l
    i = l.index('LINK_LIBRARIES')+1
    assert l[i:i+2] == ['Boost', 'Lib']
    assert 'INCLUDE_DIRS' in l
    assert l[l.index('INCLUDE_DIRS')+1] == 'Boost'

    hdr = cmakelists.find('god_build_headers')
    lib = cmakelists.find('gaudi_add_library')
    dct = cmakelists.find('god_build_dictionary')
    assert hdr < lib and lib < dct, "wrong order of calls"

def test_god_5():
    requirements = '''
package Test
version v1r0

apply_pattern god_headers files=../xml/*.xml
macro TestObj2Doth_GODflags " -s ../Test/ "
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_headers", cmakelists)
    assert len(calls) == 1, "god_build_headers wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'xml/*.xml'
    assert 'DESTINATION' in l
    assert l[l.index('DESTINATION')+1] == 'Test'

def test_god_6():
    requirements = '''
package Test
version v1r0

apply_pattern god_headers files=../xml/*.xml
macro TestObj2Doth_GODflags " -s ../src/ "
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_headers", cmakelists)
    assert len(calls) == 1, "god_build_headers wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'xml/*.xml'
    assert 'PRIVATE' in l
    assert 'DESTINTAION' not in l

def test_god_7():
    requirements = '''
package Test
version v1r0

document customdict TestCustomDict ../dict/TestCustomDict.h

apply_pattern god_dictionary files=../xml/*.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("include", cmakelists)
    assert calls
    l = calls[0].strip()
    assert l == 'GaudiObjDesc'

    calls = getCalls("god_build_dictionary", cmakelists)
    assert len(calls) == 1, "god_build_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['xml/*.xml', 'EXTEND', 'dict/TestCustomDict.h']

def test_reflex():
    requirements = '''
package Test
version v1r0

use ROOT v* LCG_Interfaces

apply_pattern reflex_dictionary \\
              dictionary=Test \\
              headerfiles=$(TESTROOT)/dict/TestDict.h \\
              selectionfile=$(TESTROOT)/dict/TestDict.xml

apply_pattern reflex_dictionary \\
              dictionary=Test2 \\
              headerfiles=$(TESTROOT)/dict/Test2Dict.h \\
              selectionfile=$(TESTROOT)/dict/Test2Dict.xml \\
              options="-DOPTION"
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_dictionary", cmakelists)
    assert len(calls) == 2, "gaudi_add_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0:3] == ['Test', 'dict/TestDict.h', 'dict/TestDict.xml']
    assert 'LINK_LIBRARIES' in l
    assert l[l.index('LINK_LIBRARIES')+1] == 'ROOT'
    assert 'INCLUDE_DIRS' in l
    assert l[l.index('INCLUDE_DIRS')+1] == 'ROOT'

    l = calls[1].strip().split()
    assert l[0:3] == ['Test2', 'dict/Test2Dict.h', 'dict/Test2Dict.xml']
    assert 'LINK_LIBRARIES' in l
    assert l[l.index('LINK_LIBRARIES')+1] == 'ROOT'
    assert 'INCLUDE_DIRS' in l
    assert l[l.index('INCLUDE_DIRS')+1] == 'ROOT'
    assert 'OPTIONS' in l
    assert l[l.index('OPTIONS')+1:] == ['"-DOPTION"']


def test_reflex_2():
    requirements = '''
package Test
version v1r0

use ROOT v* LCG_Interfaces

library Test *.ccp
apply_pattern component_library library=Test

apply_pattern reflex_dictionary \\
              dictionary=Test \\
              headerfiles=$(TESTROOT)/dict/TestDict.h \\
              selectionfile=$(TESTROOT)/dict/TestDict.xml
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 1, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Test'

    calls = getCalls("gaudi_add_dictionary", cmakelists)
    assert len(calls) == 1, "gaudi_add_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0:3] == ['Test', 'dict/TestDict.h', 'dict/TestDict.xml']

def test_reflex_3():
    requirements = '''
package Test
version v1r0

use ROOT v* LCG_Interfaces
use COOL v* LCG_Interfaces -no_auto_imports
use CORAL v* LCG_Interfaces -no_auto_imports
use Boost v* LCG_Interfaces -no_auto_imports

library Test *.ccp
apply_pattern component_library library=Test

apply_pattern reflex_dictionary \\
              dictionary=Test \\
              headerfiles=$(TESTROOT)/dict/TestDict.h \\
              selectionfile=$(TESTROOT)/dict/TestDict.xml \\
              imports="COOL -import=CORAL -import=Boost"
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 1, "gaudi_add_module wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'Test'

    calls = getCalls("gaudi_add_dictionary", cmakelists)
    assert len(calls) == 1, "gaudi_add_dictionary wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0:3] == ['Test', 'dict/TestDict.h', 'dict/TestDict.xml']
    assert 'INCLUDE_DIRS' in l
    i = l.index('INCLUDE_DIRS')
    assert 'LINK_LIBRARIES' in l
    j = l.index('LINK_LIBRARIES')
    assert set(l[i+1:j]) == set(['ROOT', 'COOL', 'CORAL', 'Boost'])
    assert set(l[j+1:]) == set(['ROOT', 'COOL', 'CORAL', 'Boost'])

def test_linkopts():
    requirements = '''
package Test
version v1r0

use ROOT v* LCG_Interfaces
use Boost v* LCG_Interfaces

macro_append ROOT_linkopts " -lMathCore"
macro_append Boost_linkopts " $(Boost_linkopts_filesystem)"

    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 2, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['Boost', 'COMPONENTS', 'filesystem'] # find_package are sorted

    l = calls[1].strip().split()
    assert l == ['ROOT', 'COMPONENTS', 'MathCore'] # find_package are sorted

def test_application():
    requirements = '''
package Test
version v1r0

application MyApp1 ../src/app1/*.cpp

application MyApp2 -group=tests ../src/app2/*.cpp

application MyApp3 -check ../src/app3/*.cpp

application MyApp4 ../tests/src/app4.cpp

application MyTestApp app5a.cpp app5b.cpp
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_executable", cmakelists)
    assert len(calls) == 5, "gaudi_add_executable wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l[0] == 'MyApp1'
    assert l[1:] == ['src/app1/*.cpp']

    l = calls[1].strip().split()
    assert l[0] == 'MyApp2'
    assert l[1:] == ['src/app2/*.cpp']

    l = calls[2].strip().split()
    assert l[0] == 'MyApp3'
    assert l[1:] == ['src/app3/*.cpp']

    l = calls[3].strip().split()
    assert l[0] == 'MyApp4'
    assert l[1:] == ['tests/src/app4.cpp']

    l = calls[4].strip().split()
    assert l[0] == 'MyTestApp'
    assert l[1:] == ['src/app5a.cpp', 'src/app5b.cpp']

    calls = getCalls("if", cmakelists)
    assert calls == ['GAUDI_BUILD_TESTS'] * 4

def test_pyqt_patterns():
    requirements = '''
package Test
version v1r0

use pygraphics v* LCG_Interfaces -no_auto_imports
use Qt v* LCG_Interfaces -no_auto_imports

apply_pattern install_python_modules

apply_pattern PyQtResource qrc_files=../qt_resources/*.qrc outputdir=../python/Test/QtApp
apply_pattern PyQtUIC ui_files=../qt_resources/*.ui outputdir=../python/Test/QtApp
macro_append Test_python_dependencies " PyQtResource PyQtUIC "
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gen_pyqt_resource", cmakelists)
    assert len(calls) == 1, "gen_pyqt_resource wrong count %d" % len(calls)
    l = calls[0].strip().split()
    assert l == ['Test.QtApp.Resources', 'Test/QtApp', 'qt_resources/*.qrc']

    calls = getCalls("gen_pyqt_uic", cmakelists)
    assert len(calls) == 1, "gen_pyqt_uic wrong count %d" % len(calls)
    l = calls[0].strip().split()
    assert l == ['Test.QtApp.UI', 'Test/QtApp', 'qt_resources/*.ui']


def test_line_cont():
    requirements = '''
package Test
version v1r0

library Test *.ccp

macro TEST "value" \\

apply_pattern component_library library=Test
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("gaudi_add_module", cmakelists)
    assert len(calls) == 1, "gaudi_add_module wrong count %d" % len(calls)


def test_line_copy_relax():
    requirements = '''
package Test
version v1r0

use RELAX         v* LCG_Interfaces

copy_relax_rootmap dict=CLHEP
copy_relax_rootmap dict=HepMC
copy_relax_rootmap dict=STL
copy_relax_rootmap dict=Math
    '''
    pkg = PackWrap("Test", requirements, files={})

    cmakelists = pkg.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 1, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['RELAX', 'REQUIRED', 'COMPONENTS', 'CLHEP', 'HepMC', 'STL', 'Math']

    calls = getCalls("add_custom_target", cmakelists)
    assert len(calls) == 1, "add_custom_target wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['RelaxRootmap', 'ALL', 'DEPENDS', '${rootmapfile}']

    # No need to check every call, just that the sequence is there


def test_project():
    proj_cmt = '''
project LHCB

use GAUDI    GAUDI_v23r4
use DBASE
use PARAM

build_strategy with_installarea
setup_strategy root
    '''
    files = {"LHCbSys": {"cmt": {"requirements": "version v35r2"}}}
    proj = ProjWrap("LHCb", proj_cmt, files=files)

    cmakelists = proj.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 1, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['GaudiProject']

    calls = getCalls("gaudi_project", cmakelists)
    assert len(calls) == 1, "gaudi_project wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['LHCb', 'v35r2', 'USE', 'Gaudi', 'v23r4']

def test_data_pkg_1():
    proj_cmt = '''
project TestProject
    '''
    files = {"TestProjectSys": {"cmt": {"requirements": "version v1r0"}},
             "Package1": {"cmt": {"requirements":
'''
version v1r0

use DtPkg        v7r* Another
use DataPack     v*
use SpecialThing *
'''}},
             }
    proj = ProjWrap("TestProject", proj_cmt, files=files)

    cmakelists = proj.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 1, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['GaudiProject']

    calls = getCalls("gaudi_project", cmakelists)
    assert len(calls) == 1, "gaudi_project wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['TestProject', 'v1r0', 'DATA',
                 'Another/DtPkg', 'VERSION', 'v7r*',
                 'DataPack',
                 'SpecialThing']

def test_data_pkg_2():
    proj_cmt = '''
project TestProject
    '''
    files = {"TestProjectSys": {"cmt": {"requirements": "version v1r0"}},
             "Package1": {"cmt": {"requirements":
'''
version v1r0

use DataPack     v*
'''}},
             "Package2": {"cmt": {"requirements":
'''
version v1r0

use SpecialThing *
'''}},
             }
    proj = ProjWrap("TestProject", proj_cmt, files=files)

    cmakelists = proj.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 1, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['GaudiProject']

    calls = getCalls("gaudi_project", cmakelists)
    assert len(calls) == 1, "gaudi_project wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['TestProject', 'v1r0', 'DATA',
                 'DataPack',
                 'SpecialThing']

def test_data_pkg_3():
    proj_cmt = '''
project TestProject
    '''
    files = {"TestProjectSys": {"cmt": {"requirements": "version v1r0"}},
             "Package1": {"cmt": {"requirements":
'''
version v1r0

use DataPack     v7r*
'''}},
             "Package2": {"cmt": {"requirements":
'''
version v1r0

use DataPack     v*
use DtPkg v1r0 Another
'''}},
             }
    proj = ProjWrap("TestProject", proj_cmt, files=files)

    cmakelists = proj.generate()
    print cmakelists

    calls = getCalls("find_package", cmakelists)
    assert len(calls) == 1, "find_package wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['GaudiProject']

    calls = getCalls("gaudi_project", cmakelists)
    assert len(calls) == 1, "gaudi_project wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['TestProject', 'v1r0', 'DATA',
                 'Another/DtPkg', 'VERSION', 'v1r0',
                 'DataPack', 'VERSION', 'v7r*']

def test_heptools_1():
    # check the case of LCGCMT in the project.cmt
    proj_cmt = '''
project TestProjectHT

use LCGCMT LCGCMT_64a
    '''
    files = {"TestProjectHTSys": {"cmt": {"requirements": "version v1r0"}}}
    proj = ProjWrap("TestProjectHT", proj_cmt, files=files)

    k = repr(('TestProjectHT', 'v1r0'))
    assert k not in cmt2cmake.cache

    toolchain = proj.generateToolchain()
    print toolchain

    calls = getCalls("set", toolchain)
    assert len(calls) == 2, "set wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['heptools_version', '64a']

    assert k in cmt2cmake.cache
    assert cmt2cmake.cache[k] == {'heptools': '64a'}

def test_heptools_2():
    # check the case of LCGCMT in a used project (already in the cache)
    proj_cmt = '''
project TestProjectHT

use BASEPROJECT BASEPROJECT_v1r0
    '''
    files = {"TestProjectHTSys": {"cmt": {"requirements": "version v2r0"}}}
    proj = ProjWrap("TestProjectHT", proj_cmt, files=files)

    k = repr(('TestProjectHT', 'v2r0'))
    assert k not in cmt2cmake.cache

    toolchain = proj.generateToolchain()
    print toolchain

    calls = getCalls("set", toolchain)
    assert len(calls) == 2, "set wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['heptools_version', '65']

    assert k in cmt2cmake.cache
    assert cmt2cmake.cache[k] == {'heptools': '65'}

def test_heptools_3():
    # check the case of LCGCMT not declared, but in the cache for us
    proj_cmt = '''
project TestProjectHT
    '''
    files = {"TestProjectHTSys": {"cmt": {"requirements": "version v3r0"}}}
    proj = ProjWrap("TestProjectHT", proj_cmt, files=files)

    k = repr(('TestProjectHT', 'v3r0'))
    assert k in cmt2cmake.cache

    toolchain = proj.generateToolchain()
    print toolchain

    calls = getCalls("set", toolchain)
    assert len(calls) == 2, "set wrong count %d" % len(calls)

    l = calls[0].strip().split()
    assert l == ['heptools_version', '23']

    assert k in cmt2cmake.cache
    assert cmt2cmake.cache[k] == {'heptools': '23'}

def test_heptools_4():
    # check the case of LCGCMT not found
    proj_cmt = '''
project TestProjectHT
    '''
    files = {"TestProjectHTSys": {"cmt": {"requirements": "version v4r0"}}}
    proj = ProjWrap("TestProjectHT", proj_cmt, files=files)

    k = repr(('TestProjectHT', 'v4r0'))
    assert k not in cmt2cmake.cache

    toolchain = proj.generateToolchain()
    assert toolchain is None

    assert k not in cmt2cmake.cache



from nose.core import main
main()
