# - Try to find COOL
# Defines:
#
#  COOL_FOUND
#  COOL_INCLUDE_DIR
#  COOL_INCLUDE_DIRS (not cached)
#  COOL_<component>_LIBRARY
#  COOL_<component>_FOUND
#  COOL_LIBRARIES (not cached)
#  COOL_LIBRARY_DIRS (not cached)
#  COOL_PYTHON_PATH
#  COOL_BINARY_PATH (not cached)


# Enforce a minimal list if none is explicitly requested
if(NOT COOL_FIND_COMPONENTS)
  set(COOL_FIND_COMPONENTS CoolKernel CoolApplication)
endif()

foreach(component ${COOL_FIND_COMPONENTS})
  find_library(COOL_${component}_LIBRARY NAMES lcg_${component})
  if (COOL_${component}_LIBRARY)
    set(COOL_${component}_FOUND 1)
    list(APPEND COOL_LIBRARIES ${COOL_${component}_LIBRARY})

    get_filename_component(libdir ${COOL_${component}_LIBRARY} PATH)
    list(APPEND COOL_LIBRARY_DIRS ${libdir})
  else()
    set(COOL_${component}_FOUND 0)
  endif()
endforeach()

if(COOL_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES COOL_LIBRARY_DIRS)
endif()

find_path(COOL_INCLUDE_DIR CoolKernel/IDatabase.h)
set(COOL_INCLUDE_DIRS ${COOL_INCLUDE_DIR})

find_path(COOL_PYTHON_PATH PyCool/__init__.py)

find_program(COOL_ReplicateDB_EXECUTABLE coolReplicateDB)
mark_as_advanced(COOL_ReplicateDB_EXECUTABLE)
if(COOL_ReplicateDB_EXECUTABLE)
  get_filename_component(COOL_BINARY_PATH ${COOL_ReplicateDB_EXECUTABLE} PATH)
endif()

# handle the QUIETLY and REQUIRED arguments and set COOL_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(COOL DEFAULT_MSG COOL_INCLUDE_DIR COOL_LIBRARIES COOL_PYTHON_PATH)

mark_as_advanced(COOL_FOUND COOL_INCLUDE_DIR COOL_PYTHON_PATH)
