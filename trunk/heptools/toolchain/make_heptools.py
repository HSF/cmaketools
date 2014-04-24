#!/usr/bin/env python
"""
Small tool to generate the heptools toolchain from a given LCGCMT.
"""
__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import os
import re

class HepToolsGenerator(object):
    """
    Class wrapping the details needed to generate the toolchain file from LCGCMT.
    """
    __header__ = """cmake_minimum_required(VERSION 2.8.5)

# Declare the version of HEP Tools we use
# (must be done before including heptools-common to allow evolution of the
# structure)
set(heptools_version  %s)

include(${CMAKE_CURRENT_LIST_DIR}/heptools-common.cmake)

# please keep alphabetic order and the structure (tabbing).
# it makes it much easier to edit/read this file!
"""
    __trailer__ = """
# Prepare the search paths according to the versions above
LCG_prepare_paths()"""

    __AA_projects__ = ("COOL", "CORAL", "RELAX", "ROOT")

    __special_dirs__ = {"CLHEP": "clhep",
                        "fftw": "fftw3",
                        "Frontier_Client": "frontier_client",
                        "GCCXML":  "gccxml",
                        "Qt":  "qt",
                        "CASTOR":  "castor",
                        "lfc": "Grid/LFC",
                        "TBB":  "tbb",
                        }

    __special_names__ = {"qt": "Qt"}

    def __init__(self, lcgcmt_root):
        """
        Prepare the instance.

        @param lcgcmt_root: path to the root directory of a given LCGCMT version
        """
        self.lcgcmt_root = lcgcmt_root

    def __repr__(self):
        """
        Representation of the instance.
        """
        return "HepToolsGenerator(%r)" % self.lcgcmt_root

    @property
    def versions(self):
        """
        Extract the external names and versions from an installed LCGCMT.

        @return: dictionary mapping external names to versions
        """
        from itertools import imap
        def statements(lines):
            """
            Generator of CMT statements from a list of lines.
            """
            statement = "" # we start with an empty statement
            for l in imap(lambda l: l.rstrip(), lines): # CMT ignores spaces at the end of line when checking for '\'
                # append the current line to the statement so far
                statement += l
                if statement.endswith("\\"):
                    # in this case we need  to strip the '\' and continue the concatenation
                    statement = statement[:-1]
                else:
                    # we can stop concatenating, but we return only non-trivial statements
                    statement = statement.strip()
                    if statement:
                        yield statement
                        statement = "" # we start collecting a new statement

        def tokens(statement):
            """
            Split a statement in tokens.

            Trivial implementation assuming the tokens do not contain spaces.
            """
            return statement.split()

        def macro(args):
            """
            Analyze the arguments of a macro command.

            @return: tuple (name, value, exceptionsDict)
            """
            unquote = lambda s: s.strip('"')
            name = args[0]
            value = unquote(args[1])
            # make a dictionary of the even to odd remaining args (unquoting the values)
            exceptions = dict(zip(args[2::2],
                                  map(unquote, args[3::2])))
            return name, value, exceptions

        # prepare the dictionary for the results
        versions = {}
        # We extract the statements from the requirements file of the LCG_Configuration package
        req = open(os.path.join(self.lcgcmt_root, "LCG_Configuration", "cmt", "requirements"))
        for toks in imap(tokens, statements(req)):
            if toks.pop(0) == "macro": # get only the macros ...
                name, value, exceptions = macro(toks)
                if name.endswith("_config_version"): # that end with _config_version
                    name = name[:-len("_config_version")]
                    name = self.__special_names__.get(name, name)
                    for tag in ["target-slc"]: # we use the alternative for 'target-slc' if present
                        value = exceptions.get(tag, value)
                    versions[name] = value.replace('(', '{').replace(')', '}')
        return versions

    def _content(self):
        """
        Generator producing the content (in blocks) of the toolchain file.
        """
        versions = self.versions

        yield self.__header__ % versions.pop("LCG")

        yield "\n# Application Area Projects"
        for name in self.__AA_projects__:
            # the width of the first string is bound to the length of the names
            # in self.__AA_projects__
            yield "LCG_AA_project(%-5s %s)" % (name, versions.pop(name))

        yield "\n# Compilers"
        # @FIXME: to be made cleaner and more flexible
        for compiler in [("gcc43", "gcc", "4.3.5"),
                         ("gcc46", "gcc", "4.6.2"),
                         ("gcc47", "gcc", "4.7.2"),
                         ("clang30", "clang", "3.0"),
                         ("gccmax", "gcc", "4.7.2")]:
            yield "LCG_compiler(%s %s %s)" % compiler

        yield "\n# Externals"
        lengths = (max(map(len, versions.keys())),
                   max(map(len, versions.values())),
                   max(map(len, self.__special_dirs__.values()))
                   )
        template = "LCG_external_package(%%-%ds %%-%ds %%-%ds)" % lengths

        def packageSorting(pkg):
            "special package sorting keys"
            key = pkg.lower()
            if key == "javajni":
                key = "javasdk_javajni"
            return key
        for name in sorted(versions.keys(), key=packageSorting):
            # special case
            if name == "uuid":
                yield "if(NOT ${LCG_OS}${LCG_OS_VERS} STREQUAL slc6) # uuid is not distributed with SLC6"
            # LCG_external_package(CLHEP            1.9.4.7             clhep)
            yield template % (name, versions[name], self.__special_dirs__.get(name, ""))
            if name == "uuid":
                yield "endif()"

        yield self.__trailer__

    def __str__(self):
        """
        Return the content of the toolchain file.
        """
        return "\n".join(self._content())

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print "Usage : %s <path to LCGCMT version>" % os.path.basename(sys.argv[0])
        sys.exit(1)
    print HepToolsGenerator(sys.argv[1])
