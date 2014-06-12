# - Find the ROOT libraries, headers and tools.
# Components:
#   Core RIO Hist Tree TreePlayer Cintex Matrix GenVector MathCore MathMore XMLIO


if(ROOT_OVERRIDE_PATH)
  if(NOT ROOTSYS AND NOT ENV{ROOTSYS})
    message(FATAL_ERROR "You must specify ROOTSYS in conjunction with ROOT_OVERRIDE_PATH.")
  endif()
  #message(STATUS "Overriding CMAKE_PREFIX_PATH looking for ROOT")
  set(ROOT_OVERRIDE_PATH NO_CMAKE_PATH)
endif()

# Find ROOTSYS
#  We assume TROOT.h is in $ROOTSYS/include
if(NOT ROOT_INCLUDE_DIR)
  find_path(ROOT_INCLUDE_DIR TROOT.h
            HINTS ${ROOTSYS}/include $ENV{ROOTSYS}/include
            PATH_SUFFIXES root root/include
            ${ROOT_OVERRIDE_PATH})
  if(ROOT_INCLUDE_DIR)
    if(ROOT_INCLUDE_DIR MATCHES "include$")
      # ROOTSYS-style installation
      get_filename_component(ROOTSYS ${ROOT_INCLUDE_DIR} PATH)
      set(ROOTSYS ${ROOTSYS} CACHE PATH "Location of the installation of ROOT" FORCE)
    else()
      set(ROOT_NO_ROOTSYS TRUE CACHE BOOL "ROOT is installed with system packages and not in a ROOTSYS")
    endif()
  endif()
endif()

set(ROOT_INCLUDE_DIRS ${ROOT_INCLUDE_DIR})

if(NOT ROOT_VERSION_STRING)
  file(STRINGS ${ROOT_INCLUDE_DIR}/RVersion.h _RVersion REGEX "define *ROOT_RELEASE ")
  string(REGEX MATCH "\"(([0-9]+)\\.([0-9]+)/([0-9]+)[a-z]*)\"" _RVersion ${_RVersion})
  set(ROOT_VERSION_STRING ${CMAKE_MATCH_1} CACHE INTERNAL "Version of ROOT")
  set(ROOT_VERSION_MAJOR ${CMAKE_MATCH_2} CACHE INTERNAL "Major version of ROOT")
  set(ROOT_VERSION_MINOR ${CMAKE_MATCH_3} CACHE INTERNAL "Minor version of ROOT")
  set(ROOT_VERSION_PATCH ${CMAKE_MATCH_4} CACHE INTERNAL "Patch version of ROOT")
endif()

# list of variable that should be checked
set(_root_required_vars ROOT_INCLUDE_DIR ROOT_VERSION_STRING)

if(${ROOT_VERSION_MAJOR}.${ROOT_VERSION_MINOR} VERSION_LESS 5.99)
  include(${CMAKE_CURRENT_LIST_DIR}/EnableROOT5.cmake)
else()
  include(${CMAKE_CURRENT_LIST_DIR}/EnableROOT6.cmake)
endif()

# handle the QUIETLY and REQUIRED arguments and set ROOT_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ROOT DEFAULT_MSG ${_root_required_vars})
mark_as_advanced(ROOT_FOUND ROOTSYS ROOT_INCLUDE_DIR)

######################################################################
# Report findings
if(ROOT_FOUND)
  if (NOT ROOT_FIND_QUIETLY AND (_found_components OR _found_tools))
    message(STATUS "ROOT version: ${ROOT_VERSION_STRING}")
    if(_found_components)
      message(STATUS "Found the following ROOT libraries:")
      foreach(component ${_found_components})
        message(STATUS "  ${component}")
      endforeach()
    endif()
    if(_found_tools)
      message(STATUS "Found the following ROOT tools:")
      foreach(component ${_found_tools})
        message(STATUS "  ${component}")
      endforeach()
    endif()
  endif()
  set(_found_components)
  set(_found_tools)
endif()

# Setting variables for the environment.
if(ROOTSYS)
  set(ROOT_ENVIRONMENT SET ROOTSYS ${ROOTSYS})
  set(ROOT_BINARY_PATH ${ROOTSYS}/bin)
  set(ROOT_LIBRARY_DIRS ${ROOTSYS}/lib)

  if(WIN32)
    set(ROOT_PYTHON_PATH ${ROOTSYS}/bin)
  else()
    set(ROOT_PYTHON_PATH ${ROOTSYS}/lib)
  endif()
endif()
