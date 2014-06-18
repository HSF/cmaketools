# - Try to find CORAL
# Defines:
#
#  CORAL_FOUND
#  CORAL_INCLUDE_DIR
#  CORAL_INCLUDE_DIRS (not cached)
#  CORAL_<component>_LIBRARY
#  CORAL_<component>_FOUND
#  CORAL_LIBRARIES (not cached)
#  CORAL_LIBRARY_DIRS (not cached)
#  CORAL_PYTHON_PATH
#  CORAL_BINARY_PATH (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT CORAL_FIND_COMPONENTS)
  set(CORAL_FIND_COMPONENTS CoralBase)
endif()

foreach(component ${CORAL_FIND_COMPONENTS})
  find_library(CORAL_${component}_LIBRARY NAMES lcg_${component})
  if (CORAL_${component}_LIBRARY)
    set(CORAL_${component}_FOUND 1)
    list(APPEND CORAL_LIBRARIES ${CORAL_${component}_LIBRARY})

    get_filename_component(libdir ${CORAL_${component}_LIBRARY} PATH)
    list(APPEND CORAL_LIBRARY_DIRS ${libdir})
  else()
    set(CORAL_${component}_FOUND 0)
  endif()
  mark_as_advanced(CORAL_${component}_LIBRARY)
endforeach()

if(CORAL_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES CORAL_LIBRARY_DIRS)
endif()

find_path(CORAL_INCLUDE_DIR RelationalAccess/ConnectionService.h)
find_path(CORAL_PYTHON_PATH coral.py)

set(CORAL_INCLUDE_DIRS ${CORAL_INCLUDE_DIR})

find_program(CORAL_coralServer_EXECUTABLE coralServer)
mark_as_advanced(CORAL_coralServer_EXECUTABLE)
if(CORAL_coralServer_EXECUTABLE)
  get_filename_component(CORAL_BINARY_PATH ${CORAL_coralServer_EXECUTABLE} PATH)
endif()

# handle the QUIETLY and REQUIRED arguments and set CORAL_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(CORAL DEFAULT_MSG CORAL_INCLUDE_DIR CORAL_LIBRARIES CORAL_PYTHON_PATH)

mark_as_advanced(CORAL_FOUND CORAL_INCLUDE_DIR CORAL_PYTHON_PATH)
