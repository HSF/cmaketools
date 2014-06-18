# - Try to find Pythia6
# Defines:
#
#  PYTHIA6_FOUND
#  PYTHIA6_INCLUDE_DIR
#  PYTHIA6_INCLUDE_DIRS (not cached)
#  PYTHIA6_<component>_LIBRARY
#  PYTHIA6_<component>_FOUND
#  PYTHIA6_LIBRARIES (not cached)
#  PYTHIA6_LIBRARY_DIRS (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT Pythia6_FIND_COMPONENTS)
  set(Pythia6_FIND_COMPONENTS pythia6 pythia6_dummy)
endif()

foreach(component ${Pythia6_FIND_COMPONENTS})
  find_library(PYTHIA6_${component}_LIBRARY NAMES ${component}
               HINTS $ENV{PYTHIA6_ROOT_DIR}/lib ${PYTHIA6_ROOT_DIR}/lib)
  if (PYTHIA6_${component}_LIBRARY)
    set(PYTHIA6_${component}_FOUND 1)
    list(APPEND PYTHIA6_LIBRARIES ${PYTHIA6_${component}_LIBRARY})

    get_filename_component(libdir ${PYTHIA6_${component}_LIBRARY} PATH)
    list(APPEND PYTHIA6_LIBRARY_DIRS ${libdir})
  else()
    set(PYTHIA6_${component}_FOUND 0)
  endif()
  mark_as_advanced(PYTHIA6_${component}_LIBRARY)
endforeach()

if(PYTHIA6_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES PYTHIA6_LIBRARY_DIRS)
endif()

find_path(PYTHIA6_INCLUDE_DIR general_pythia.inc
          HINTS $ENV{PYTHIA6_ROOT_DIR}/include ${PYTHIA6_ROOT_DIR}/include)
set(PYTHIA6_INCLUDE_DIRS ${PYTHIA6_INCLUDE_DIR})
mark_as_advanced(PYTHIA6_INCLUDE_DIR)

# handle the QUIETLY and REQUIRED arguments and set PYTHIA6_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Pythia6 DEFAULT_MSG PYTHIA6_INCLUDE_DIR PYTHIA6_LIBRARIES CMAKE_Fortran_COMPILER)

mark_as_advanced(PYTHIA6_FOUND)
