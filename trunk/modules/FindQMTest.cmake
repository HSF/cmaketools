# - Find QMTest.
#
# This module will define the following variables:
#  QMTEST_EXECUTABLE  - the qmtest main script
#  QMTEST_PYTHON_PATH - directory containing the Python module 'qm'

find_program(QMTEST_EXECUTABLE
  NAMES qmtest
  PATHS ${QMtest_home}/bin
        ${QMtest_home}/Scripts
  HINTS ${QMTEST_ROOT_DIR}/bin
        $ENV{QMTEST_ROOT_DIR}/bin
)

get_filename_component(QMTEST_BINARY_PATH ${QMTEST_EXECUTABLE} PATH)
get_filename_component(QMTEST_PREFIX_PATH ${QMTEST_BINARY_PATH} PATH)

find_path(QMTEST_PYTHON_PATH
  NAMES qm/__init__.py
  PATHS
   ${QMTEST_PREFIX_PATH}/lib/python${Python_config_version_twodigit}/site-packages
   ${QMTEST_PREFIX_PATH}/Lib/site-packages
)

if (NOT QMTEST_PYTHON_PATH)
  # let's try to find the qm module in the standard environment
  find_package(PythonInterp)
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import os, qm; print os.path.dirname(os.path.dirname(qm.__file__))"
                  OUTPUT_VARIABLE QMTEST_PYTHON_PATH OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
  if (QMTEST_PYTHON_PATH)
    # we found it, so no need to extend the PYTHONPATH
    set(QMTEST_PYTHON_PATH ${QMTEST_PYTHON_PATH} CACHE "" "" FORCE)
  endif()
endif()

# handle the QUIETLY and REQUIRED arguments and set COOL_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(QMTest DEFAULT_MSG QMTEST_EXECUTABLE QMTEST_PYTHON_PATH)

mark_as_advanced(QMTEST_EXECUTABLE QMTEST_PYTHON_PATH)


set(QMTEST_ENVIRONMENT SET QM_home ${QMTEST_PREFIX_PATH})

if(WIN32)
  set(QMTEST_LIBRARY_PATH ${QMTEST_PREFIX_PATH}/Lib/site-packages/pywin32_system32)
endif()
