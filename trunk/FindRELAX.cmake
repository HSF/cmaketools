# - Locate RELAX libraries directory.
# Defines:
#
#  RELAX_FOUND
#  RELAX_<component>_LIBRARY
#  RELAX_<component>_ROOTMAP
#  RELAX_ROOTMAPS (not cached) list of rootmap files required
#  RELAX_LIBRARY_DIRS (not cached)
#  RELAX_FOUND_COMPONENTS (not cached)

# Enforce a minimal list if none is explicitly requested
if(NOT RELAX_FIND_COMPONENTS)
  set(RELAX_FIND_COMPONENTS STL)
endif()

set(RELAX_ROOTMAP_SUFFIX .pamtoor)

set(RELAX_ROOTMAPS)

foreach(component ${RELAX_FIND_COMPONENTS})

  find_library(RELAX_${component}_LIBRARY NAMES ${component}Rflx
               HINTS $ENV{RELAX_ROOT_DIR}/lib ${RELAX_ROOT_DIR}/lib )
  mark_as_advanced(RELAX_${component}_LIBRARY)

  if(RELAX_${component}_LIBRARY)
    list(APPEND RELAX_FOUND_COMPONENTS ${component})
    get_filename_component(libdir ${RELAX_${component}_LIBRARY} PATH)
    list(APPEND RELAX_LIBRARY_DIRS ${libdir})
    # deduce the name of the rootmap file for the library
    string(REPLACE "${CMAKE_SHARED_MODULE_SUFFIX}" "${RELAX_ROOTMAP_SUFFIX}" RELAX_${component}_ROOTMAP "${RELAX_${component}_LIBRARY}")
    list(APPEND RELAX_ROOTMAPS ${RELAX_${component}_ROOTMAP})
  endif()
endforeach()
if(RELAX_LIBRARY_DIRS)
  list(REMOVE_DUPLICATES RELAX_LIBRARY_DIRS)
endif()

# handle the QUIETLY and REQUIRED arguments and set RELAX_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(RELAX DEFAULT_MSG RELAX_LIBRARY_DIRS RELAX_ROOTMAPS)

mark_as_advanced(RELAX_FOUND)
