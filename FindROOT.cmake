# - Find the ROOT libraries, headers and tools.
# Components:
#   Core Cint Reflex RIO Hist Tree TreePlayer Cintex Matrix GenVector MathCore MathMore XMLIO


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
            ${ROOT_OVERRIDE_PATH})
  get_filename_component(ROOTSYS ${ROOT_INCLUDE_DIR} PATH)
  set(ROOTSYS ${ROOTSYS} CACHE PATH "Location of the installation of ROOT" FORCE)
endif()

set(ROOT_INCLUDE_DIRS ${ROOTSYS}/include)
set(ROOT_LIBRARY_DIRS ${ROOTSYS}/lib)

# This is the list of all known component libraries
set(ROOT_ALL_COMPONENTS Core Cint Reflex RIO Hist Tree TreePlayer Cintex Matrix GenVector MathCore MathMore XMLIO)
# and build tools
set(ROOT_ALL_TOOLS genreflex genmap root)

# Helper macro to discover the dependencies between components needed on Mac)
macro(_root_get_deps libpath var)
  # reset output var
  set(${var})
  if(APPLE)
    get_filename_component(_libname ${libpath} NAME)
    # get all required libraries
    execute_process(COMMAND otool -L ${libpath}
                    OUTPUT_VARIABLE _otool_out)
    # find all the libs taken from @rpath (they come from ROOT)
    string(REGEX MATCHALL "@rpath/lib[^ ]*\\.so" _otool_out "${_otool_out}")
    # remove the current library (if present)
    list(REMOVE_ITEM _otool_out "@rpath/${_libname}")
    # translate to a list of component names
    set(${var})
    foreach(_c ${_otool_out})
      string(REPLACE "@rpath/lib" "" _c ${_c})
      string(REPLACE ".so" "" _c ${_c})
      list(APPEND ${var} ${_c})
    endforeach()
  endif()
endmacro()

# Enforce a minimal list if none is explicitly requested
if(NOT ROOT_FIND_COMPONENTS)
  set(ROOT_FIND_COMPONENTS Core)
endif()

# Locate the libraries (forcing few default ones)
while(ROOT_FIND_COMPONENTS)
  # pop the first element from the list
  list(GET ROOT_FIND_COMPONENTS 0 component)
  list(REMOVE_AT ROOT_FIND_COMPONENTS 0)
  # look for the library if not found yet
  if(NOT ROOT_${component}_LIBRARY)
    find_library(ROOT_${component}_LIBRARY NAMES ${component}
                 HINTS ${ROOT_LIBRARY_DIRS}
                 ${ROOT_OVERRIDE_PATH})
    if(ROOT_${component}_LIBRARY)
      mark_as_advanced(ROOT_${component}_LIBRARY)
      set(_found_components ${_found_components} ${component})
    endif()
  endif()
  if(APPLE)
    if(ROOT_${component}_LIBRARY AND NOT DEFINED ROOT_${component}_DEPS)
      #message(STATUS "scanning dependencies of ${component} (${ROOT_${component}_LIBRARY})")
      _root_get_deps(${ROOT_${component}_LIBRARY} ROOT_${component}_DEPS)
      #message(STATUS "found: ${ROOT_${component}_DEPS}")
      set(ROOT_${component}_DEPS ${ROOT_${component}_DEPS} CACHE INTERNAL "Components ${component} depends on.")
    endif()
    list(APPEND ROOT_FIND_COMPONENTS ${ROOT_${component}_DEPS})
    list(REMOVE_DUPLICATES ROOT_FIND_COMPONENTS)
  endif()
  #message(STATUS "ROOT_FIND_COMPONENTS=${ROOT_FIND_COMPONENTS}")
  set(ROOT_LIBRARIES ${ROOT_LIBRARIES} ${ROOT_${component}_LIBRARY})
endwhile()

# Locate the tools
foreach(component ${ROOT_ALL_TOOLS})
  if(NOT ROOT_${component}_CMD)
    find_program(ROOT_${component}_CMD ${component}
                 HINTS ${ROOTSYS}/bin
                 ${ROOT_OVERRIDE_PATH})
    if(ROOT_${component}_CMD)
      mark_as_advanced(ROOT_${component}_CMD)
      set(_found_tools ${_found_tools} ${component})
    endif()
  endif()
endforeach()

# handle the QUIETLY and REQUIRED arguments and set ROOT_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ROOT DEFAULT_MSG ROOTSYS ROOT_INCLUDE_DIR)
mark_as_advanced(ROOT_FOUND ROOTSYS ROOT_INCLUDE_DIR)

######################################################################
# Report findings
if(ROOT_FOUND)
  if(NOT ROOT_VERSION_STRING)
    file(STRINGS ${ROOT_INCLUDE_DIR}/RVersion.h _RVersion REGEX "define *ROOT_RELEASE ")
    string(REGEX MATCH "\"(([0-9]+)\\.([0-9]+)/([0-9]+)[a-z]*)\"" _RVersion ${_RVersion})
    set(ROOT_VERSION_STRING ${CMAKE_MATCH_1} CACHE INTERNAL "Version of ROOT")
    set(ROOT_VERSION_MAJOR ${CMAKE_MATCH_2} CACHE INTERNAL "Major version of ROOT")
    set(ROOT_VERSION_MINOR ${CMAKE_MATCH_3} CACHE INTERNAL "Minor version of ROOT")
    set(ROOT_VERSION_PATCH ${CMAKE_MATCH_4} CACHE INTERNAL "Patch version of ROOT")
  endif()
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

################################################################################
# Useful functions
################################################################################
include(CMakeParseArguments)

#-------------------------------------------------------------------------------
# reflex_generate_dictionary(dictionary headerfile selectionfile OPTIONS opt1 opt2 ...)
#
# Generate a Reflex dictionary library from the specified header and selection.
#-------------------------------------------------------------------------------
macro(reflex_generate_dictionary dictionary _headerfile _selectionfile)
  find_package(GCCXML)
  if(NOT GCCXML)
    message(FATAL_ERROR "GCCXML not found, cannot generate Reflex dictionaries.")
  endif()

  CMAKE_PARSE_ARGUMENTS(ARG "" "" "OPTIONS" ${ARGN})

  # Ensure that the path to the header and selection files are absolute
  if(IS_ABSOLUTE ${_selectionfile})
   set(selectionfile ${_selectionfile})
  else()
   set(selectionfile ${CMAKE_CURRENT_SOURCE_DIR}/${_selectionfile})
  endif()
  if(IS_ABSOLUTE ${_headerfile})
    set(headerfiles ${_headerfile})
  else()
    set(headerfiles ${CMAKE_CURRENT_SOURCE_DIR}/${_headerfile})
  endif()

  set(gensrcdict ${dictionary}_dict.cpp)

  if(NOT MSVC)
    set(GCCXML_CXX_COMPILER ${CMAKE_CXX_COMPILER} CACHE STRING "Compiler that GCCXML must use.")
  else()
    set(GCCXML_CXX_COMPILER cl CACHE STRING "Compiler that GCCXML must use.")
  endif()
  mark_as_advanced(GCCXML_CXX_COMPILER)
  set(gccxmlopts "--gccxml-compiler ${GCCXML_CXX_COMPILER}")

  if(GCCXML_CXX_FLAGS)
    set(gccxmlopts "${gccxmlopts} --gccxml-cxxflags ${GCCXML_CXX_FLAGS}")
  endif()

  set(rootmapname ${dictionary}Dict.rootmap)
  set(rootmapopts --rootmap=${rootmapname})
  if (NOT WIN32)
    set(rootmapopts ${rootmapopts} --rootmap-lib=lib${dictionary}Dict)
  else()
    set(rootmapopts ${rootmapopts} --rootmap-lib=${dictionary}Dict)
  endif()

  #set(include_dirs -I${CMAKE_CURRENT_SOURCE_DIR})
  get_directory_property(_incdirs INCLUDE_DIRECTORIES)
  foreach(d ${CMAKE_CURRENT_SOURCE_DIR} ${_incdirs})
   set(include_dirs ${include_dirs} -I${d})
  endforeach()

  get_directory_property(_defs COMPILE_DEFINITIONS)
  foreach(d ${_defs})
   set(definitions ${definitions} -D${d})
  endforeach()

  if(gccxmlopts)
    set(gccxmlopts "--gccxmlopt=${gccxmlopts}")
  endif()

  get_filename_component(GCCXML_home ${GCCXML} PATH)
  add_custom_command(
    OUTPUT ${gensrcdict} ${rootmapname}
    COMMAND ${ROOT_genreflex_CMD}
         ${headerfiles} -o ${gensrcdict} ${gccxmlopts} ${rootmapopts} --select=${selectionfile}
         --gccxmlpath=${GCCXML_home} ${ARG_OPTIONS} ${include_dirs} ${definitions}
    DEPENDS ${headerfiles} ${selectionfile})

  # Creating this target at ALL level enables the possibility to generate dictionaries (genreflex step)
  # well before the dependent libraries of the dictionary are build
  add_custom_target(${dictionary}Gen ALL DEPENDS ${gensrcdict} ${rootmapname})

  set_property(TARGET ${dictionary}Gen PROPERTY ROOTMAPFILE ${rootmapname})

endmacro()

#-------------------------------------------------------------------------------
# reflex_dictionary(dictionary headerfile selectionfile OPTIONS opt1 opt2 ...)
#
# Generate and build a Reflex dictionary library from the specified header and selection.
#-------------------------------------------------------------------------------
function(reflex_dictionary dictionary headerfile selectionfile)
  CMAKE_PARSE_ARGUMENTS(ARG "" "" "LINK_LIBRARIES;OPTIONS" ${ARGN})
  # ensure that we split on the spaces
  separate_arguments(ARG_OPTIONS)
  reflex_generate_dictionary(${dictionary} ${headerfile} ${selectionfile} OPTIONS ${ARG_OPTIONS})
  add_library(${dictionary}Dict MODULE ${gensrcdict})
  target_link_libraries(${dictionary}Dict ${ARG_LINK_LIBRARIES} ${ROOT_Reflex_LIBRARY})
  # ensure that *Gen and *Dict are not built at the same time
  add_dependencies(${dictionary}Dict ${dictionary}Gen)
  # Attach the name of the rootmap file to the target so that it can be used from
  set_property(TARGET ${dictionary}Dict PROPERTY ROOTMAPFILE ${rootmapname})
endfunction()


macro (ROOT_GENERATE_DICTIONARY INFILES LINKDEF_FILE OUTFILE INCLUDE_DIRS_IN)
  set(INCLUDE_DIRS)
  foreach (_current_FILE ${INCLUDE_DIRS_IN})
    set(INCLUDE_DIRS ${INCLUDE_DIRS} -I${_current_FILE})
  endforeach (_current_FILE ${INCLUDE_DIRS_IN})
  STRING(REGEX REPLACE "^(.*)\\.(.*)$" "\\1.h" bla "${OUTFILE}")
  SET (OUTFILES ${OUTFILE} ${bla})
  if (CMAKE_SYSTEM_NAME MATCHES Linux)
    ADD_CUSTOM_COMMAND(OUTPUT ${OUTFILES}
    COMMAND LD_LIBRARY_PATH=${ROOT_LIBRARY_DIR} ROOTSYS=${ROOTSYS} ${ROOT_CINT_EXECUTABLE}
    ARGS -f ${OUTFILE} -c -DHAVE_CONFIG_H ${INCLUDE_DIRS} ${INFILES} ${LINKDEF_FILE}
    DEPENDS ${INFILES} ${LINKDEF_FILE})
  else (CMAKE_SYSTEM_NAME MATCHES Linux)
    if (CMAKE_SYSTEM_NAME MATCHES Darwin)
    ADD_CUSTOM_COMMAND(
      OUTPUT ${OUTFILES}
      COMMAND DYLD_LIBRARY_PATH=${ROOT_LIBRARY_DIR} ROOTSYS=${ROOTSYS} ${ROOT_CINT_EXECUTABLE}
      ARGS -f ${OUTFILE} -c -DHAVE_CONFIG_H ${INCLUDE_DIRS} ${INFILES} ${LINKDEF_FILE}
      DEPENDS ${INFILES} ${LINKDEF_FILE} )
    endif (CMAKE_SYSTEM_NAME MATCHES Darwin)
  endif (CMAKE_SYSTEM_NAME MATCHES Linux)
endmacro (ROOT_GENERATE_DICTIONARY)

set(ROOT_ENVIRONMENT SET ROOTSYS ${ROOTSYS})
set(ROOT_BINARY_PATH ${ROOTSYS}/bin)

if(WIN32)
  set(ROOT_PYTHON_PATH ${ROOTSYS}/bin)
else()
  set(ROOT_PYTHON_PATH ${ROOTSYS}/lib)
endif()
