Instructions for the cmt2cmake.py tool
======================================

Introduction
------------
The script ``cmt2cmake.py`` is a tool that can convert the configuration of a
CMT_ project based on Gaudi_ to the equivalent one for CMake.

This tools have limitations: it cannot cover all the possible cases, so, in some
(hopefully few) circumstances, there is the need for manual adaptation of the
generated files.

To be noted that ``cmt2cmake.py`` doesn't use CMT and, instead of analyzing what
CMT_ would do, it parses the configuration files (``requirements``) to try to
understand what the developer wanted to do. Because of this approach, it
requires a cache with the information collected for the projects the one to be
converted depends on.  This cache has to be in the same directory as the script
and can be easily generated running the script on all the required projects.

Usage
-----
The usage is simple: just go to the top directory of the project to be converted
and call the script.

For example, to process LHCb, one has to prepare the cache for the information
of Gaudi::

    $ python cmt2cmake.py --cache-only /path/to/Gaudi

The next step is to translate LHCb::

    $ python cmt2cmake.py --cache-only /path/to/LHCb
    $ python cmt2cmake.py /path/to/LHCb

The first call updates the cache so that it can be used for the
interdependencies of the packages in LHCb.

Configuration
-------------
Some packages need special treatment. Few cases are supported:

    - `ignored_packages`: packages that should not treated at all
    - `data_packages`: known data packages, cannot be used in dependencies
    - `needing_python`: packages that need to link against Python
    - `no_pedantic`: packages that cannot compile of the -pedantic option is used
    - `ignore_env`: special environment variables that should not be set in CMake

The configuration required for the conversion of a project can be stored in a
JSON file called `cmt2cmake.cfg` at the top level directory of the project.

It must be noted that `ignored_packages` and `data_packages` require the full
name of the package (hat+name) while the others use only the simple package name
(without hat).

Testing
-------
This directory contains also the tests for ``cmt2cmake.py``, written for
nosetests_. To run the tests it is enough to go to the directory containing
``cmt2cmake.py`` and call the nosetests command::

    $ cd /path/to/cmt2cmake
    $ nosetests -v --with-doctest


Note
----
The parsing of CMT ``requirements`` files is implemented using the module
``pyparsing``_. To simplify the use of the script, a copy of it is available
together with the script itself.


.. _CMT: http://www.cmtsite.org
.. _CMake: http://www.cmake.org
.. _Gaudi: http://cern.ch/gaudi
.. _pyparsing: http://pyparsing.wikispaces.com
.. _nosetests: http://nose.readthedocs.org

