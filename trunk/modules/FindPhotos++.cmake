# - Try to find Photos++
# Defines:
#
#  PHOTOS++_FOUND
#  PHOTOS++_INCLUDE_DIR
#  PHOTOS++_INCLUDE_DIRS (not cached)
#  PHOTOS++_<component>_LIBRARY
#  PHOTOS++_<component>_FOUND
#  PHOTOS++_LIBRARIES (not cached)
#  PHOTOS++_LIBRARY_DIRS (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT PHOTOS++_FIND_COMPONENTS)
  set(PHOTOS++_FIND_COMPONENTS Fortran CxxInterface)
endif()

foreach(component ${PHOTOS++_FIND_COMPONENTS})
  find_library(PHOTOS++_${component}_LIBRARY NAMES Photos${component}
               HINTS ${PHOTOS++_ROOT_DIR}/lib
                     $ENV{PHOTOSPP_ROOT_DIR}/lib
                     ${PHOTOSPP_ROOT_DIR}/lib)
  if (PHOTOS++_${component}_LIBRARY)
    set(PHOTOS++_${component}_FOUND 1)
    list(APPEND PHOTOS++_LIBRARIES ${PHOTOS++_${component}_LIBRARY})

    get_filename_component(libdir ${PHOTOS++_${component}_LIBRARY} PATH)
    list(APPEND PHOTOS++_LIBRARY_DIRS ${libdir})
  else()
    set(PHOTOS++_${component}_FOUND 0)
  endif()
  mark_as_advanced(PHOTOS++_${component}_LIBRARY)
endforeach()

if(PHOTOS++_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES PHOTOS++_LIBRARY_DIRS)
endif()

find_path(PHOTOS++_INCLUDE_DIR Photos/Photos.h
          HINTS ${PHOTOS++_ROOT_DIR}/include
                $ENV{PHOTOSPP_ROOT_DIR}/include
                ${PHOTOSPP_ROOT_DIR}/include)
set(PHOTOS++_INCLUDE_DIRS ${PHOTOS++_INCLUDE_DIR})
mark_as_advanced(PHOTOS++_INCLUDE_DIR)

# handle the QUIETLY and REQUIRED arguments and set PHOTOS++_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Photos++ DEFAULT_MSG PHOTOS++_INCLUDE_DIR PHOTOS++_LIBRARIES)

mark_as_advanced(PHOTOS++_FOUND)
