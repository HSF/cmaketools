# - Try to find ALPGEN
# Defines:
#
#  ALPGEN_FOUND
#  ALPGEN_INCLUDE_DIR
#  ALPGEN_INCLUDE_DIRS (not cached)
#  ALPGEN_<component>_LIBRARY
#  ALPGEN_<component>_FOUND
#  ALPGEN_LIBRARIES (not cached)
#  ALPGEN_LIBRARY_DIRS (not cached)
#  ALPGEN_PYTHON_PATH
#  ALPGEN_BINARY_PATH (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT ALPGEN_FIND_COMPONENTS)
  set(ALPGEN_FIND_COMPONENTS alpgen alpsho)
endif()

foreach(component ${ALPGEN_FIND_COMPONENTS})
  find_library(ALPGEN_${component}_LIBRARY NAMES ${component})
  if (ALPGEN_${component}_LIBRARY)
    set(ALPGEN_${component}_FOUND 1)
    list(APPEND ALPGEN_LIBRARIES ${ALPGEN_${component}_LIBRARY})

    get_filename_component(libdir ${ALPGEN_${component}_LIBRARY} PATH)
    list(APPEND ALPGEN_LIBRARY_DIRS ${libdir})
  else()
    set(ALPGEN_${component}_FOUND 0)
  endif()
  mark_as_advanced(ALPGEN_${component}_LIBRARY)
endforeach()

if(ALPGEN_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES ALPGEN_LIBRARY_DIRS)
endif()

find_file(ALPGEN_AUTHOR_DIR alpgen-author
          HINTS ${ALPGEN_LIBRARY_DIRS}
          PATH_SUFFIXES ../../share)
mark_as_advanced(ALPGEN_AUTHOR_DIR)
set(ALPGEN_INCLUDE_DIRS ${ALPGEN_AUTHOR_DIR} ${ALPGEN_AUTHOR_DIR}/alplib)

# handle the QUIETLY and REQUIRED arguments and set ALPGEN_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ALPGEN DEFAULT_MSG ALPGEN_LIBRARY_DIRS ALPGEN_LIBRARIES ALPGEN_AUTHOR_DIR)

mark_as_advanced(ALPGEN_FOUND)

set(ALPGEN_ENVIRONMENT SET ALPGEN_AUTHOR_DIR "${ALPGEN_AUTHOR_DIR}")
