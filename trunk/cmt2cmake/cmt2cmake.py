#!/usr/bin/env python
"""
Script to convert CMT projects/packages to CMake Gaudi-based configuration.
"""
import os
import sys
import re
import logging
import shelve
import json
import operator

def makeParser(patterns=None):
    from pyparsing import ( Word, QuotedString, Keyword, Literal, SkipTo, StringEnd,
                            ZeroOrMore, Optional, Combine,
                            alphas, alphanums, printables )
    dblQuotedString = QuotedString(quoteChar='"', escChar='\\', unquoteResults=False)
    sglQuotedString = QuotedString(quoteChar="'", escChar='\\', unquoteResults=False)
    value = dblQuotedString | sglQuotedString | Word(printables)

    tag_name = Word(alphas + "_", alphanums + "_-")
    tag_expression = Combine(tag_name + ZeroOrMore('&' + tag_name))
    values = value + ZeroOrMore(tag_expression + value)

    identifier = Word(alphas + "_", alphanums + "_")
    variable = Combine(identifier + '=' + value)

    constituent_option = (Keyword('-no_share')
                          | Keyword('-no_static')
                          | Keyword('-prototypes')
                          | Keyword('-no_prototypes')
                          | Keyword('-check')
                          | Keyword('-target_tag')
                          | Combine('-group=' + value)
                          | Combine('-suffix=' + value)
                          | Combine('-import=' + value)
                          | variable
                          | Keyword('-OS9')
                          | Keyword('-windows'))
    source = (Word(alphanums + "_*./$()")
              | Combine('-s=' + value)
              | Combine('-k=' + value)
              | Combine('-x=' + value))

    # statements
    comment = (Literal("#") + SkipTo(StringEnd())).suppress()

    package = Keyword('package') + Word(printables)
    version = Keyword("version") + Word(printables)
    use = Keyword("use") + identifier + Word(printables) + Optional(identifier) + Optional(Keyword("-no_auto_imports"))

    constituent = ((Keyword('library') | Keyword('application') | Keyword('document'))
                   + identifier + ZeroOrMore(constituent_option | source))
    macro = (Keyword('macro') | Keyword('macro_append')) + identifier + values
    setenv = (Keyword('set') | Keyword('path_append') | Keyword('path_prepend')) + identifier + values

    apply_pattern = Keyword("apply_pattern") + identifier + ZeroOrMore(variable)
    if patterns:
        direct_patterns = reduce(operator.or_, map(Keyword, set(patterns)))
        # add the implied 'apply_pattern' to the list of tokens
        direct_patterns.addParseAction(lambda toks: toks.insert(0, 'apply_pattern'))
        apply_pattern = apply_pattern | (direct_patterns + ZeroOrMore(variable))

    statement = (package | version | use | constituent | macro | setenv | apply_pattern)

    return Optional(statement) + Optional(comment) + StringEnd()


cache = None
def open_cache():
    global cache
    # record of known subdirs with their libraries
    # {'<subdir>': {'libraries': [...]}}
    # it contains some info about the projects too, under the keys like repr(('<project>', '<version>'))
    try:
        # First we try the environment variable CMT2CMAKECACHE and the directory
        # containing this file...
        _shelve_file = os.environ.get('CMT2CMAKECACHE',
                                      os.path.join(os.path.dirname(__file__),
                                                   '.cmt2cmake.cache'))
        cache = shelve.open(_shelve_file)
    except:
        # ... otherwise we use the user home directory
        _shelve_file = os.path.join(os.path.expanduser('~'), '.cmt2cmake.cache')
        #logging.info("Using cache file %s", _shelve_file)
        cache = shelve.open(_shelve_file)

def close_cache():
    global cache
    if cache:
        cache.close()
        cache = None

config = {}
for k in ['ignored_packages', 'data_packages', 'needing_python', 'no_pedantic',
          'ignore_env']:
    config[k] = set()

# mappings
ignored_packages = config['ignored_packages']
data_packages = config['data_packages']

# List of packages known to actually need Python to build
needing_python = config['needing_python']

# packages that must have the pedantic option disabled
no_pedantic = config['no_pedantic']

ignore_env = config['ignore_env']

def loadConfig(config_file):
    '''
    Merge the content of the JSON file with the configuration dictionary.
    '''
    global config
    if os.path.exists(config_file):
        data = json.load(open(config_file))
        for k in data:
            if k not in config:
                config[k] = set()
            config[k].update(map(str, data[k]))
        # print config

loadConfig(os.path.join(os.path.dirname(__file__), 'cmt2cmake.cfg'))

def extName(n):
    '''
    Mapping between the name of the LCG_Interface name and the Find*.cmake name
    (if non-trivial).
    '''
    mapping = {'Reflex': 'ROOT',
               'Python': 'PythonLibs',
               'neurobayes_expert': 'NeuroBayesExpert',
               'mysql': 'MySQL',
               'oracle': 'Oracle',
               'sqlite': 'SQLite',
               'lfc': 'LFC',
               'fftw': 'FFTW',
               'uuid': 'UUID',
               'fastjet': 'FastJet',
               }
    return mapping.get(n, n)

def isPackage(path):
    return os.path.isfile(os.path.join(path, "cmt", "requirements"))

def isProject(path):
    return os.path.isfile(os.path.join(path, "cmt", "project.cmt"))

def projectCase(name):
    return {'DAVINCI': 'DaVinci',
            'LHCB': 'LHCb'}.get(name.upper(), name.capitalize())

def callStringWithIndent(cmd, arglines):
    '''
    Produce a string for a call of a command with indented arguments.

    >>> print callStringWithIndent('example_command', ['arg1', 'arg2', 'arg3'])
    example_command(arg1
                    arg2
                    arg3)
    >>> print callStringWithIndent('example_command', ['', 'arg2', 'arg3'])
    example_command(arg2
                    arg3)
    '''
    indent = '\n' + ' ' * (len(cmd) + 1)
    return cmd + '(' + indent.join(filter(None, arglines)) + ')'

def writeToFile(filename, data, log=None):
    '''
    Write the generated CMakeLists.txt.
    '''
    if log and os.path.exists(filename):
        log.info('overwriting %s', filename)
    f = open(filename, "w")
    f.write(data)
    f.close()

class Package(object):
    def __init__(self, path, project=None):
        self.path = os.path.realpath(path)
        if not isPackage(self.path):
            raise ValueError("%s is not a package" % self.path)

        self.name = os.path.basename(self.path)
        self.requirements = os.path.join(self.path, "cmt", "requirements")
        self.project = project

        # prepare attributes filled during parsing of requirements
        self.uses = {}
        self.version = None
        self.libraries = []
        self.applications = []
        self.documents = []
        self.macros = {}
        self.sets = {}
        self.paths = {}

        # These are patterns that can appear only once per package.
        # The corresponding dictionary will contain the arguments passed to the
        # pattern.
        self.singleton_patterns = set(["QMTest", "install_python_modules", "install_scripts",
                                       "install_more_includes", "god_headers", "god_dictionary",
                                       "PyQtResource", "PyQtUIC"])
        self.install_more_includes = {}
        self.install_python_modules = self.install_scripts = self.QMTest = False
        self.god_headers = {}
        self.god_dictionary = {}
        self.PyQtResource = {}
        self.PyQtUIC = {}

        # These are patterns that can be repeated in the requirements.
        # The corresponding data members will contain the list of dictionaries
        # corresponding to the various calls.
        self.multi_patterns = set(['reflex_dictionary', 'component_library', 'linker_library',
                                   'copy_relax_rootmap'])
        self.reflex_dictionary = []
        self.component_library = []
        self.linker_library = []
        self.copy_relax_rootmap = []

        self.reflex_dictionaries = {}
        self.component_libraries = set()
        self.linker_libraries = set()

        self.log = logging.getLogger('Package(%s)' % self.name)
        self.CMTParser = makeParser(self.singleton_patterns | self.multi_patterns)
        try:
            self._parseRequirements()
        except:
            print "Processing %s" % self.requirements
            raise
        # update the known subdirs
        cache[self.name] = {# list of linker libraries provided by the package
                            'libraries': list(self.linker_libraries),
                            # true if it's a headers-only package
                            'includes': bool(self.install_more_includes and
                                             not self.linker_libraries)}

    def generate(self):
        # header
        data = ["#" * 80,
                "# Package: %s" % self.name,
                "#" * 80,
                "gaudi_subdir(%s %s)" % (self.name, self.version),
                ""]
        # dependencies
        #  subdirectories (excluding specials)
        subdirs = [n for n in sorted(self.uses)
                   if not n.startswith("LCG_Interfaces/")
                      and n not in ignored_packages
                      and n not in data_packages]

        inc_dirs = []
        if subdirs:
            # check if we are missing info for a subdir
            missing_subdirs = set([s.rsplit('/')[-1] for s in subdirs]) - set(cache)
            if missing_subdirs:
                self.log.warning('Missing info cache for subdirs %s', ' '.join(sorted(missing_subdirs)))
            # declare inclusion order
            data.append(callStringWithIndent('gaudi_depends_on_subdirs', subdirs))
            data.append('')
            # consider header-only subdirs
            #  for each required subdir that comes with only headers, add its
            #  location to the call to 'include_directories'
            inc_only = lambda s: cache.get(s.rsplit('/')[-1], {}).get('includes')
            inc_dirs = filter(inc_only, subdirs)


        #  externals (excluding specials)
        #  - Python needs to be treated in a special way
        find_packages = {}
        for n in sorted(self.uses):
            if n.startswith("LCG_Interfaces/"):
                n = extName(n[15:])
                # FIXME: find a general way to treat these special cases
                if n == "PythonLibs":
                    if self.name not in needing_python: # only these packages actually link against Python
                        continue
                # get custom link options
                linkopts = self.macros.get(n + '_linkopts', '')
                components = [m.group(1) or m.group(2)
                              for m in re.finditer(r'(?:\$\(%s_linkopts_([^)]*)\))|(?:-l(\w*))' % n,
                                                   linkopts)]
                # FIXME: find a general way to treat the special cases
                if n == 'COOL':
                    components = ['CoolKernel', 'CoolApplication']
                elif n == 'CORAL':
                    components = ['CoralBase', 'CoralKernel', 'RelationalAccess']
                elif n == 'RELAX' and self.copy_relax_rootmap:
                    components = [d['dict'] for d in self.copy_relax_rootmap if 'dict' in d]

                find_packages[n] = find_packages.get(n, []) + components

        # this second loops avoid double entries do to converging results of extName()
        for n in sorted(find_packages):
            args = [n]
            components = find_packages[n]
            if components:
                if n == 'RELAX': # FIXME: probably we should set 'REQUIRED' for all the externals
                    args.append('REQUIRED')
                args.append('COMPONENTS')
                args.extend(components)
            data.append('find_package(%s)' % ' '.join(args))
        if find_packages:
            data.append("")

        if self.name in no_pedantic:
            data.append('string(REPLACE "-pedantic" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")\n')

        # the headers can be installed via "PUBLIC_HEADERS" or by hand
        if self.install_more_includes:
            headers = [d for d in self.install_more_includes.values()
                       if os.path.isdir(os.path.join(self.path, d))]
        else:
            headers = []

        if self.god_headers or self.god_dictionary:
            data.append("include(GaudiObjDesc)")
            data.append("")

        god_headers_dest = None
        if self.god_headers:
            godargs = [self.god_headers["files"].replace("../", "")]

            godflags = self.macros.get('%sObj2Doth_GODflags' % self.name, "")
            godflags = re.search(r'-s\s*(\S+)', godflags)
            if godflags:
                god_headers_dest = os.path.normpath('Event/' + godflags.group(1))
                if god_headers_dest == 'src':
                    # special case
                    godargs.append('PRIVATE')
                else:
                    godargs.append('DESTINATION ' + god_headers_dest)

            data.append(callStringWithIndent('god_build_headers', godargs))
            data.append("")

        god_dict = []
        if self.god_dictionary:
            god_dict = [('--GOD--',
                        [self.god_dictionary["files"].replace("../", "")],
                        None, [])]

        rflx_dict = []
        for d in self.reflex_dictionary:
            for k in d:
                v = d[k]
                v = v.replace("$(%sROOT)/" % self.name.upper(), "")
                v = v.replace("../", "")
                d[k] = v
            imports = [i.strip('"').replace('-import=', '') for i in d.get('imports', '').strip().split()]
            rflx_dict.append((d['dictionary'] + 'Dict',
                              [d['headerfiles'], d['selectionfile']],
                              None,
                              imports))

        # libraries
        global_imports = [extName(name[15:])
                          for name in self.uses
                          if name.startswith('LCG_Interfaces/') and self.uses[name][1]] # list of imported ext
        if 'PythonLibs' in global_imports and self.name not in needing_python:
            global_imports.remove('PythonLibs')

        subdir_imports = [s.rsplit('/')[-1] for s in subdirs if self.uses[s][1]]
        local_links = [] # keep track of linker libraries found so far
        applications_names = set([a[0] for a in self.applications])
        # Note: a god_dictionary, a reflex_dictionary or an application is like a module
        for name, sources, group, imports in self.libraries + god_dict + rflx_dict + self.applications:
            isGODDict = isRflxDict = isComp = isApp = isLinker = False
            if name == '--GOD--':
                isGODDict = True
                name = '' # no library name for GOD dictionaries
            elif name.endswith('Dict') and name[:-4] in self.reflex_dictionaries:
                isRflxDict = True
                name = name[:-4]
            elif name in self.component_libraries:
                isComp = True
            elif name in applications_names:
                isApp = True
            else:
                if name not in self.linker_libraries:
                    self.log.warning('library %s not declared as component or linker, assume linker', name)
                isLinker = True

            # prepare the bits of the command: cmd, name, sources, args
            if isComp:
                cmd = 'gaudi_add_module'
            elif isGODDict:
                cmd = 'god_build_dictionary'
            elif isRflxDict:
                cmd = 'gaudi_add_dictionary'
            elif isApp:
                cmd = 'gaudi_add_executable'
            else: # i.e. isLinker (a fallback)
                cmd = 'gaudi_add_library'

            if not sources:
                self.log.warning("Missing sources for target %s", name)

            args = []
            if isLinker:
                if headers:
                    args.append('PUBLIC_HEADERS ' + ' '.join(headers))
                else:
                    args.append('NO_PUBLIC_HEADERS')
            elif isGODDict:
                if god_headers_dest:
                    args.append('HEADERS_DESTINATION ' + god_headers_dest)
                # check if we have a customdict in the documents
                for docname, _, docsources in self.documents:
                    if docname == 'customdict':
                        args.append('EXTEND ' + docsources[0].replace('../', ''))
                        break


            # # collection of link libraries. #
            # Externals and subdirs are treated differently:
            # - externals: just use the package name
            # - subdirs: find the exported libraries in the global var cache
            # We also have to add the local linker libraries.

            # separate external and subdir explicit imports
            subdirsnames = [s.rsplit('/')[-1] for s in subdirs]
            subdir_local_imports = [i for i in imports if i in subdirsnames]
            ext_local_imports = [extName(i) for i in imports if i not in subdir_local_imports]

            # prepare the link list with the externals
            links = global_imports + ext_local_imports
            if links or inc_dirs:
                # external links need the include dirs
                args.append('INCLUDE_DIRS ' + ' '.join(links + inc_dirs))

            if links:
                not_included = set(links).difference(find_packages, set([s.rsplit('/')[-1] for s in subdirs]))
                if not_included:
                    self.log.warning('imports without use: %s', ', '.join(sorted(not_included)))

            # add subdirs...
            for s in subdir_imports + subdir_local_imports:
                if s in cache:
                    links.extend(cache[s]['libraries'])
            # ... and local libraries
            links.extend(local_links)
            if 'AIDA' in links:
                links.remove('AIDA') # FIXME: AIDA does not have a library

            if links:
                # note: in some cases we get quoted library names
                args.append('LINK_LIBRARIES ' + ' '.join([l.strip('"') for l in links]))

            if isRflxDict and self.reflex_dictionaries[name]:
                args.append('OPTIONS ' + self.reflex_dictionaries[name])

            if isLinker:
                local_links.append(name)

            # FIXME: very very special case :(
            if name == 'garbage' and self.name == 'FileStager':
                data.append('# only for the applications\nfind_package(Boost COMPONENTS program_options)\n')

            # write command
            if not (isGODDict or isRflxDict):
                # dictionaries to not need to have the paths fixed
                sources = [os.path.normpath('src/' + s) for s in sources]
            # FIXME: special case
            sources = [s.replace('src/$(GAUDICONFROOT)', '${CMAKE_SOURCE_DIR}/GaudiConf') for s in sources]
            libdata = callStringWithIndent(cmd, [name] + sources + args)

            # FIXME: wrap the test libraries in one if block (instead of several)
            if group in ('tests', 'test'):
                # increase indentation
                libdata = ['  ' + l for l in libdata.splitlines()]
                # and wrap
                libdata.insert(0, 'if(GAUDI_BUILD_TESTS)')
                libdata.append('endif()')
                libdata = '\n'.join(libdata)
            data.append(libdata)
            data.append('') # empty line

        # PyQt resources and UIs
        if self.PyQtResource or self.PyQtUIC:
            data.append("# gen_pyqt_* functions are provided by 'pygraphics'")
        if self.PyQtResource:
            qrc_files = self.PyQtResource["qrc_files"].replace("../", "")
            qrc_dest = self.PyQtResource["outputdir"].replace("../python/", "")
            qrc_target = qrc_dest.replace('/', '.') + '.Resources'
            data.append('gen_pyqt_resource(%s %s %s)' % (qrc_target, qrc_dest, qrc_files))
        if self.PyQtUIC:
            ui_files = self.PyQtUIC["ui_files"].replace("../", "")
            ui_dest = self.PyQtUIC["outputdir"].replace("../python/", "")
            ui_target = qrc_dest.replace('/', '.') + '.UI'
            data.append('gen_pyqt_uic(%s %s %s)' % (ui_target, ui_dest, ui_files))
        if self.PyQtResource or self.PyQtUIC:
            data.append('') # empty line

        if self.copy_relax_rootmap:
            data.extend(['# Merge the RELAX rootmaps',
                         'set(rootmapfile ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/relax.rootmap)',
                         callStringWithIndent('add_custom_command',
                                              ['OUTPUT ${rootmapfile}',
                                               'COMMAND ${merge_cmd} ${RELAX_ROOTMAPS} ${rootmapfile}',
                                               'DEPENDS ${RELAX_ROOTMAPS}']),
                         'add_custom_target(RelaxRootmap ALL DEPENDS ${rootmapfile})',
                         '\n# Install the merged file',
                         'install(FILES ${rootmapfile} DESTINATION lib)\n'])

        # installation
        installs = []
        if headers and not self.linker_libraries: # not installed yet
            installs.append("gaudi_install_headers(%s)" % (" ".join(headers)))
        if self.install_python_modules:
            # if we install Python modules, we need to check if we have special
            # names for the ConfUser modules
            if (self.name + 'ConfUserModules') in self.macros:
                installs.append('set_property(DIRECTORY PROPERTY CONFIGURABLE_USER_MODULES %s)'
                                % self.macros[self.name + 'ConfUserModules'])
            installs.append("gaudi_install_python_modules()")
        if self.install_scripts:
            installs.append("gaudi_install_scripts()")
        if installs:
            data.extend(installs)
            data.append('') # empty line

        # environment
        def fixSetValue(s):
            '''
            Convert environment variable values from CMT to CMake.
            '''
            # escape '$' if not done already
            s = re.sub(r'(?<!\\)\$', '\\$', s)
            # replace parenthesis with curly braces
            s = re.sub(r'\$\(([^()]*)\)', r'${\1}', s)
            # replace variables like Package_root with PACKAGEROOT
            v = re.compile(r'\$\{(\w*)_root\}')
            m = v.search(s)
            while m:
                s = s[:m.start()] + ('${%sROOT}' % m.group(1).upper()) + s[m.end():]
                m = v.search(s)
            return s

        if self.sets:
            data.append(callStringWithIndent('gaudi_env',
                                             ['SET %s %s' % (v, fixSetValue(self.sets[v]))
                                              for v in sorted(self.sets)]))
            data.append('') # empty line

        # tests
        if self.QMTest:
            data.append("\ngaudi_add_test(QMTest QMTEST)")

        return "\n".join(data) + "\n"

    @property
    def data_packages(self):
        '''
        Return the list of data packages used by this package in the form of a
        dictionary {name: version_pattern}.
        '''
        return dict([ (n, self.uses[n][0]) for n in self.uses if n in data_packages ])

    def process(self, overwrite=None):
        cml = os.path.join(self.path, "CMakeLists.txt")
        if ((overwrite == 'force')
            or (not os.path.exists(cml))
            or ((overwrite == 'update')
                and (os.path.getmtime(cml) < os.path.getmtime(self.requirements)))):
            # write the file
            data = self.generate()
            writeToFile(cml, data, self.log)
        else:
            self.log.warning("file %s already exists", cml)

    def _parseRequirements(self):
        def requirements():
            statement = ""
            for l in open(self.requirements):
                if '#' in l:
                    l = l[:l.find('#')]
                l = l.strip()
                # if we have something in the line, extend the statement
                if l:
                    statement += l
                    if statement.endswith('\\'):
                        # if the statement requires another line, get the next
                        statement = statement[:-1] + ' '
                        continue
                # either we got something more in the statement or not, but
                # an empty line after a '\' means ending the statement
                if statement:
                    try:
                        yield list(self.CMTParser.parseString(statement))
                    except:
                        # ignore not know statements
                        self.log.debug("Failed to parse statement: %r", statement)
                    statement = ""

        for args in requirements():
            cmd = args.pop(0)
            if cmd == 'version':
                self.version = args[0]
            elif cmd == "use":
                if "-no_auto_imports" in args:
                    imp = False
                    args.remove("-no_auto_imports")
                else:
                    imp = True
                if len(args) > 1: # only one argument means usually a conditional use
                    if len(args) > 2:
                        name = "%s/%s" % (args[2], args[0])
                    else:
                        name = args[0]
                    self.uses[name] = (args[1], imp)

            elif cmd == "apply_pattern":
                pattern = args.pop(0)
                args = dict([x.split('=', 1) for x in args])
                if pattern in self.singleton_patterns:
                    setattr(self, pattern, args or True)
                elif pattern in self.multi_patterns:
                    getattr(self, pattern).append(args)

            elif cmd == 'library':
                name = args.pop(0)
                # digest arguments (options, variables, sources)
                imports = []
                group = None
                sources = []
                for a in args:
                    if a.startswith('-'): # options
                        if a.startswith('-import='):
                            imports.append(a[8:])
                        elif a.startswith('-group='):
                            group = a[7:]
                    elif '=' in a: # variable
                        pass
                    else: # source
                        sources.append(a)
                self.libraries.append((name, sources, group, imports))

            elif cmd == 'application':
                name = args.pop(0)
                # digest arguments (options, variables, sources)
                imports = []
                group = None
                sources = []
                for a in args:
                    if a.startswith('-'): # options
                        if a.startswith('-import='):
                            imports.append(a[8:])
                        elif a.startswith('-group='):
                            group = a[7:]
                        elif a == '-check': # used for test applications
                            group = 'tests'
                    elif '=' in a: # variable
                        pass
                    else: # source
                        sources.append(a)
                if 'test' in name.lower() or [s for s in sources if 'test' in s.lower()]:
                    # usually, developers do not put tests in the right group
                    group = 'tests'
                self.applications.append((name, sources, group, imports))

            elif cmd == 'document':
                name = args.pop(0)
                constituent = args.pop(0)
                sources = args
                self.documents.append((name, constituent, sources))

            elif cmd == 'macro':
                # FIXME: should handle macro tags
                name = args.pop(0)
                value = args[0].strip('"').strip("'")
                self.macros[name] = value

            elif cmd == 'macro_append':
                # FIXME: should handle macro tags
                name = args.pop(0)
                value = args[0].strip('"').strip("'")
                self.macros[name] = self.macros.get(name, "") + value

            elif cmd == 'set':
                name = args.pop(0)
                if name not in ignore_env:
                    value = args[0].strip('"').strip("'")
                    self.sets[name] = value

        # classification of libraries in the package
        unquote = lambda x: x.strip('"').strip("'")
        self.component_libraries = set([unquote(l['library']) for l in self.component_library])
        self.linker_libraries = set([unquote(l['library']) for l in self.linker_library])
        self.reflex_dictionaries = dict([(unquote(l['dictionary']), l.get('options', ''))
                                         for l in self.reflex_dictionary])

toolchain_template = '''# Special wrapper to load the declared version of the heptools toolchain.
set(heptools_version {0})

# Remove the reference to this file from the cache.
unset(CMAKE_TOOLCHAIN_FILE CACHE)

# Find the actual toolchain file.
find_file(CMAKE_TOOLCHAIN_FILE
          NAMES heptools-${{heptools_version}}.cmake
          HINTS ENV CMTPROJECTPATH
          PATHS ${{CMAKE_CURRENT_LIST_DIR}}/cmake/toolchain
          PATH_SUFFIXES toolchain)

if(NOT CMAKE_TOOLCHAIN_FILE)
  message(FATAL_ERROR "Cannot find heptools-${{heptools_version}}.cmake.")
endif()

# Reset the cache variable to have proper documentation.
set(CMAKE_TOOLCHAIN_FILE ${{CMAKE_TOOLCHAIN_FILE}}
    CACHE FILEPATH "The CMake toolchain file" FORCE)

include(${{CMAKE_TOOLCHAIN_FILE}})
'''

class Project(object):
    def __init__(self, path):
        """
        Create a project instance from the root directory of the project.
        """
        self.path = os.path.realpath(path)
        if not isProject(self.path):
            raise ValueError("%s is not a project" % self.path)
        self.requirements = os.path.join(self.path, "cmt", "project.cmt")
        # Private variables for cached properties
        self._packages = None
        self._container = None

    @property
    def packages(self):
        """
        Dictionary of packages contained in the project.
        """
        if self._packages is None:
            self._packages = {}
            for root, dirs, _files in os.walk(self.path):
                if isPackage(root):
                    p = Package(root, self)
                    name = os.path.relpath(p.path, self.path)
                    self._packages[name] = p
                    dirs[:] = []
        return self._packages

    @property
    def container(self):
        """
        Name of the container package of the project.

        The name of the container is deduced using the usual LHCb convention
        (instead of the content of project.cmt).
        """
        if self._container is None:
            for suffix in ["Release", "Sys"]:
                try:
                    # gets the first package that ends with the suffix, and does
                    # not have a hat.. or raise StopIteration
                    c = (p for p in self.packages
                         if p.endswith(suffix) and "/" not in p).next()
                    self._container = self.packages[c]
                    break
                except StopIteration:
                    pass
        return self._container

    @property
    def name(self):
        # The name of the project is the same of the container without
        # the 'Release' or 'Sys' suffixes.
        return self.container.name.replace("Release", "").replace("Sys", "")

    @property
    def version(self):
        return self.container.version

    def uses(self):
        for l in open(self.requirements):
            l = l.split()
            if l and l[0] == "use" and l[1] != "LCGCMT" and len(l) == 3:
                yield (projectCase(l[1]), l[2].rsplit('_', 1)[-1])

    def heptools(self):
        '''
        Return the version of heptools (LCGCMT) used by this project.
        '''

        def updateCache(value):
            '''
            helper function to update the cache and return the value
            '''
            k = repr((self.name, self.version))
            d = cache.get(k, {})
            d['heptools'] = value
            cache[k] = d
            return value

        # check for a direct dependency
        exp = re.compile(r'^\s*use\s+LCGCMT\s+LCGCMT[_-](\S+)')
        for l in open(self.requirements):
            m = exp.match(l)
            if m:
                return updateCache(m.group(1))

        # try with the projects we use (in the cache),
        # including ourselves (we may already be there)
        for u in list(self.uses()) + [(self.name, self.version)]:
            u = repr(u)
            if u in cache and 'heptools' in cache[u]:
                return updateCache(cache[u]['heptools'])

        # we cannot guess the version of heptools
        return None

    @property
    def data_packages(self):
        '''
        Return the list of data packages used by this project (i.e. by all the
        packages in this project) in the form of a dictionary
        {name: version_pattern}.
        '''
        # for debugging we map
        def appendDict(d, kv):
            '''
            helper function to extend a dictionary of lists
            '''
            k, v = kv
            if k in d:
                d[k].append(v)
            else:
                d[k] = [v]
            return d
        # dictionary {"data_package": ("user_package", "data_pkg_version")}
        dp2pkg = {}
        for pkgname, pkg in self.packages.items():
            for dpname, dpversion in pkg.data_packages.items():
                appendDict(dp2pkg, (dpname, (pkgname, dpversion)))

        # check and collect the data packages
        result = {}
        for dp in sorted(dp2pkg):
            versions = set([v for _, v in dp2pkg[dp]])
            if versions:
                version = sorted(versions)[-1]
            else:
                version = '*'
            if len(versions) != 1:
                logging.warning('Different versions for data package %s, using %s from %s', dp, version, dp2pkg[dp])
            result[dp] = version

        return result

    def generate(self):
        # list containing the lines to write to the file
        data = ["CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)",
                "",
                "#---------------------------------------------------------------",
                "# Load macros and functions for Gaudi-based projects",
                "find_package(GaudiProject)",
                "#---------------------------------------------------------------",
                "",
                "# Declare project name and version"]
        l = "gaudi_project(%s %s" % (self.name, self.version)
        use = "\n                  ".join(["%s %s" % u for u in self.uses()])
        if use:
            l += "\n              USE " + use
        # collect data packages
        data_pkgs = []
        for p, v in sorted(self.data_packages.items()):
            if v in ('v*', '*'):
                data_pkgs.append(p)
            else:
                data_pkgs.append("%s VERSION %s" % (p, v))
        if data_pkgs:
            l += ("\n              DATA " +
                  "\n                   ".join(data_pkgs))
        l += ")"
        data.append(l)
        return "\n".join(data) + "\n"

    def generateToolchain(self):
        heptools_version = self.heptools()
        if heptools_version:
            return toolchain_template.format(heptools_version)
        return None

    def process(self, overwrite=None):
        # Prepare the project configuration
        def produceFile(name, generator):
            cml = os.path.join(self.path, name)
            if ((overwrite == 'force')
                or (not os.path.exists(cml))
                or ((overwrite == 'update')
                    and (os.path.getmtime(cml) < os.path.getmtime(self.requirements)))):
                # write the file
                data = generator()
                if data:
                    writeToFile(cml, data, logging)
                else:
                    logging.info("file %s not generated (empty)", cml)
            else:
                logging.warning("file %s already exists", cml)

        produceFile("CMakeLists.txt", self.generate)
        produceFile("toolchain.cmake", self.generateToolchain)

        # Recurse in the packages
        for p in sorted(self.packages):
            self.packages[p].process(overwrite)


def main(args=None):
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] [path to project or package]",
                          description="Convert CMT-based projects/packages to CMake (Gaudi project)")
    parser.add_option("-f", "--force", action="store_const",
                      dest='overwrite', const='force',
                      help="overwrite existing files")
    parser.add_option('--cache-only', action='store_true',
                      help='just update the cache without creating the CMakeLists.txt files.')
    parser.add_option('-u' ,'--update', action='store_const',
                      dest='overwrite', const='update',
                      help='modify the CMakeLists.txt files if they are older than '
                           'the corresponding requirements.')
    #parser.add_option('--cache-file', action='store',
    #                  help='file to be used for the cache')

    opts, args = parser.parse_args(args=args)

    logging.basicConfig(level=logging.INFO)

    top_dir = os.getcwd()
    if args:
        top_dir = args[0]
        if not os.path.isdir(top_dir):
            parser.error("%s is not a directory" % top_dir)

    loadConfig(os.path.join(top_dir, 'cmt2cmake.cfg'))

    open_cache()
    if isProject(top_dir):
        root = Project(top_dir)
    elif isPackage(top_dir):
        root = Package(top_dir)
        if opts.cache_only:
            return # the cache is updated instantiating the package
    else:
        raise ValueError("%s is neither a project nor a package" % top_dir)

    if opts.cache_only:
        root.packages # the cache is updated by instantiating the packages
        root.heptools() # this triggers the caching of the heptools_version
        # note that we can get here only if root is a project
    else:
        root.process(opts.overwrite)
    close_cache()

if __name__ == '__main__':
    main()
    sys.exit(0)
