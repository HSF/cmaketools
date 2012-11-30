How to build and use the Gaudi with CMake
=========================================

Requirements
------------
The CMake configuration of Gaudi is based on the version 2.8.5 or later of
CMake. On lxplus (SLC5 and SLC6) you need to call::

    $ export PATH=/afs/cern.ch/sw/lcg/contrib/CMake/2.8.9/Linux-i386/bin:$PATH

You also need to ensure that the compiler you want to use is configured and
available on the PATH, for example with::

    $ . /afs/cern.ch/sw/lcg/contrib/gcc/4.6.2/$CMTCONFIG/setup.sh

.. note:: If you use the LHCb environment (as of LbScripts v7r3), you do not
   need to prepare the environment for the compiler (except for ICC and Clang).

Quick Start
-----------
To quickly get started, you can use the Makefile ``Makefile-cmake.mk``, which
will take care of the main details (except the value of ``CMTCONFIG``)::

    $ make -f Makefile-cmake.mk -j 8
    $ make -f Makefile-cmake.mk test

The main targets are:

    ``configure``
        just run CMake to generate the build directory (or reconfigure)

    ``all``
        build everything (implies ``configure``)

    ``test``
        run the tests, note that it does not imply the build and does not
        require installation

    ``install``
        populate the ``InstallArea`` directory, `required for runtime`


Build
-----
I suggest to use the off-source build, which means that the files required by
the build and the build products are created in a different directory than the
source one.
In this example I'll use ``Gaudi.build``, created at the same level as the
directory containing the sources (``Gaudi.src``).

To prepare the build directory, you have to::

    $ src=$PWD/Gaudi.src
    $ mkdir Gaudi.build
    $ cd Gaudi.build
    $ cmake -DCMAKE_TOOLCHAIN_FILE=$src/toolchain.cmake \
        -G "Eclipse CDT4 - Unix Makefiles" $src

This will create the required Unix makefiles and the Eclipse project
configuration to build Gaudi.

Other options are available on the command line when you prepare the build
directory the first time or afterwards via the CMake configuration tool
``ccmake``, for example ``CMAKE_USE_DISTCC`` or ``CMAKE_USE_CCACHE``.

Now you can build the project with a simple (from ``Gaudi.build``)::

    $ make

or from Eclipse after you imported the project.

The tests can be run via the command ``ctest`` or with ``make test``.


Install
-------
The build of the project obtained with CMake cannot be used directly by other
projects: it needs to be installed in the source directory (for backward
compatibility with CMT) with the command::

    $ make install

It must be noted that the special file ``python.zip`` is not automatically
generated, so, if you want it, you have to call, after the installation::

    $ make python.zip


Run
---
The runtime environment for the installed binaries is described by the XML file
``GaudiEnvironment.xml`` located in the directory ``InstallArea/$CMTCONFIG``, in
the format understood by the Python script ``env.py`` available in the ``cmake``
directory in the source tree (it is also installed).

The behavior of ``env.py`` is quite similar to that of the standard Unix
commmand ``env`` (see ``man env``), with the addition of few functions (append,
prepend, XML).

For example, you can call ``gaudirun.py`` like this (with the variable ``src``
defined above)::

    $ $src/cmake/env.py --xml $src/InstallArea/$CMTCONFIG/GaudiEnvironment.xml \
        gaudirun.py --help

or, to have a sub-shell with the right environment::

    $ $src/cmake/env.py --xml $src/InstallArea/$CMTCONFIG/GaudiEnvironment.xml bash


Run from the build directory
----------------------------
For testing and debugging (as already mentioned) there is no need to install.

To run an application using the build directory, you can use the script
``env.py`` with the XML file ``GaudBuildEnvironment.xml`` located in the build
directory, or the convenience script ``run`` (always in the build directory),
for example like this::

    $ cd Gaudi.build
    $ ./run gaudirun.py --help
    $ ./run bash

Resources
-------------
    * `CMake documentation <http://www.cmake.org/cmake/help/documentation.html>`_
    * ``FindTBB.cmake`` was taken from https://bitbucket.org/sergiu/tbb-cmake
