# - Try to find HIJING
# Defines:
#
#  HIJING_FOUND
#  HIJING_INCLUDE_DIR
#  HIJING_INCLUDE_DIRS (not cached)
#  HIJING_<component>_LIBRARY
#  HIJING_<component>_FOUND
#  HIJING_LIBRARIES (not cached)
#  HIJING_LIBRARY_DIRS (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT HIJING_FIND_COMPONENTS)
  set(HIJING_FIND_COMPONENTS hijing hijing_dummy)
endif()

foreach(component ${HIJING_FIND_COMPONENTS})
  find_library(HIJING_${component}_LIBRARY NAMES ${component}
               HINTS $ENV{HIJING_ROOT_DIR}/lib ${HIJING_ROOT_DIR}/lib)
  if (HIJING_${component}_LIBRARY)
    set(HIJING_${component}_FOUND 1)
    list(APPEND HIJING_LIBRARIES ${HIJING_${component}_LIBRARY})

    get_filename_component(libdir ${HIJING_${component}_LIBRARY} PATH)
    list(APPEND HIJING_LIBRARY_DIRS ${libdir})
  else()
    set(HIJING_${component}_FOUND 0)
  endif()
  mark_as_advanced(HIJING_${component}_LIBRARY)
endforeach()

if(HIJING_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES HIJING_LIBRARY_DIRS)
endif()

# handle the QUIETLY and REQUIRED arguments and set HIJING_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(HIJING DEFAULT_MSG HIJING_LIBRARIES CMAKE_Fortran_COMPILER)

mark_as_advanced(HIJING_FOUND)
