# - Locate CASTOR libraries
# Defines:
#
#  CASTOR_FOUND
#  CASTOR_INCLUDE_DIR
#  CASTOR_INCLUDE_DIRS (not cached)
#  CASTOR_<component>_LIBRARY
#  CASTOR_<component>_FOUND
#  CASTOR_LIBRARIES (not cached)
#  CASTOR_LIBRARY_DIRS (not cached)


# Enforce a minimal list if none is explicitly requested
if(NOT CASTOR_FIND_COMPONENTS)
  set(CASTOR_FIND_COMPONENTS shift)
endif()

find_path(CASTOR_INCLUDE_DIR shift.h PATH_SUFFIXES usr/include)
set(CASTOR_INCLUDE_DIRS ${CASTOR_INCLUDE_DIR})

set(CASTOR_LIBRARY_DIRS)

foreach(component ${CASTOR_FIND_COMPONENTS})
  if(component STREQUAL shift) # libshift.so is the only one without the prefix 'castor'
    set(name ${component})
  else()
    set(name castor${component})
  endif()
  find_library(CASTOR_${component}_LIBRARY NAMES ${name} PATH_SUFFIXES usr/lib64)
  if (CASTOR_${component}_LIBRARY)
    set(CASTOR_${component}_FOUND 1)
    list(APPEND CASTOR_LIBRARIES ${CASTOR_${component}_LIBRARY})

    get_filename_component(libdir ${CASTOR_${component}_LIBRARY} PATH)
    list(APPEND CASTOR_LIBRARY_DIRS ${libdir})
  else()
    set(CASTOR_${component}_FOUND 0)
  endif()
  mark_as_advanced(CASTOR_${component}_LIBRARY)
endforeach()

if(CASTOR_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES CASTOR_LIBRARY_DIRS)
endif()

# handle the QUIETLY and REQUIRED arguments and set SQLITE_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(CASTOR DEFAULT_MSG CASTOR_INCLUDE_DIR CASTOR_LIBRARIES)

mark_as_advanced(CASTOR_FOUND CASTOR_INCLUDE_DIR)
