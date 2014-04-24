# - Try to find Tauola++
# Defines:
#
#  TAUOLA++_FOUND
#  TAUOLA++_INCLUDE_DIR
#  TAUOLA++_INCLUDE_DIRS (not cached)
#  TAUOLA++_<component>_LIBRARY
#  TAUOLA++_<component>_FOUND
#  TAUOLA++_LIBRARIES (not cached)
#  TAUOLA++_LIBRARY_DIRS (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT Tauola++_FIND_COMPONENTS)
  set(Tauola++_FIND_COMPONENTS Fortran CxxInterface)
endif()

#message(STATUS "Tauola++ CMAKE_PREFIX_PATH")
#foreach(_x ${CMAKE_PREFIX_PATH})
#  message(STATUS "Tauola++ -- ${_x}")
#endforeach()

foreach(component ${Tauola++_FIND_COMPONENTS})
  find_library(TAUOLA++_${component}_LIBRARY NAMES Tauola${component}
               HINTS ${TAUOLA++_ROOT_DIR}/lib
                     $ENV{TAUOLAPP_ROOT_DIR}/lib ${TAUOLAPP_ROOT_DIR}/lib)
  if (TAUOLA++_${component}_LIBRARY)
    set(TAUOLA++_${component}_FOUND 1)
    list(APPEND TAUOLA++_LIBRARIES ${TAUOLA++_${component}_LIBRARY})

    get_filename_component(libdir ${TAUOLA++_${component}_LIBRARY} PATH)
    list(APPEND TAUOLA++_LIBRARY_DIRS ${libdir})
  else()
    set(TAUOLA++_${component}_FOUND 0)
  endif()
  mark_as_advanced(TAUOLA++_${component}_LIBRARY)
endforeach()

if(TAUOLA++_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES TAUOLA++_LIBRARY_DIRS)
endif()

find_path(TAUOLA++_INCLUDE_DIR Tauola/Tauola.h
          HINTS ${TAUOLA++_ROOT_DIR}/include
                $ENV{TAUOLAPP_ROOT_DIR}/include ${TAUOLAPP_ROOT_DIR}/include)
set(TAUOLA++_INCLUDE_DIRS ${TAUOLA++_INCLUDE_DIR})
mark_as_advanced(TAUOLA++_INCLUDE_DIR)

# handle the QUIETLY and REQUIRED arguments and set TAUOLA++_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Tauola++ DEFAULT_MSG TAUOLA++_INCLUDE_DIR TAUOLA++_LIBRARIES)

mark_as_advanced(TAUOLA++_FOUND)
