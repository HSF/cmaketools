# - Simple module to add the pytools directory to the python path
#
# PYTOOLS_FOUND
# PYTOOLS_PYTHON_PATH
# PYTOOLS_BINARY_PATH

set(PYTOOLS_FOUND 1)
set(PYTOOLS_PYTHON_PATH ${pytools_home}/lib/python${Python_config_version_twodigit}/site-packages
    CACHE PATH "Path to the pytools LCG package (Python modules)")

set(PYTOOLS_BINARY_PATH ${pytools_home}/bin
    CACHE PATH "Path to the pytools LCG package (scripts)")

mark_as_advanced(PYTOOLS_FOUND PYTOOLS_PYTHON_PATH PYTOOLS_BINARY_PATH)
