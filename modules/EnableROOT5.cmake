# Internal settings for ROOT 5

# This is the list of some known component libraries
set(ROOT_ALL_COMPONENTS Core Cint Reflex RIO Hist Tree TreePlayer Cintex Matrix
                        GenVector MathCore MathMore XMLIO Graf Gui Rint Physics)
# and build tools
set(ROOT_ALL_TOOLS genreflex genmap root rootcint)

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

macro(_find_ROOT_components)
  # Locate the libraries (forcing few default ones)
  foreach(component ${ARGN})
    if(NOT ROOT_${component}_LIBRARY)
      # pop the first element from the list
      list(APPEND _root_required_vars ROOT_${component}_LIBRARY)
      # look for the library if not found yet
      if(NOT ROOT_${component}_LIBRARY)
        find_library(ROOT_${component}_LIBRARY NAMES ${component} lib${component}
                     HINTS ${ROOTSYS}/lib
                     PATH_SUFFIXES root
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
        _find_ROOT_components(${ROOT_${component}_DEPS})
      endif()
    endif()
    #message(STATUS "ROOT_FIND_COMPONENTS=${ROOT_FIND_COMPONENTS}")
    if(ROOT_${component}_LIBRARY)
      set(ROOT_LIBRARIES ${ROOT_LIBRARIES} ${ROOT_${component}_LIBRARY})
    endif()
  endforeach()
endmacro()

# Enforce a minimal list if none is explicitly requested
_find_ROOT_components(Core ${ROOT_FIND_COMPONENTS})
if(ROOT_LIBRARIES)
  list(REMOVE_DUPLICATES ROOT_LIBRARIES)
endif()

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

if(ROOT_rootcint_CMD)
  set(ROOT_CINT_DICT_ENABLED ON)
endif()

if(ROOT_genreflex_CMD)
  set(ROOT_REFLEX_DICT_ENABLED ON)
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

  CMAKE_PARSE_ARGUMENTS(ARG "SPLIT_CLASSDEF" "" "OPTIONS" ${ARGN})

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

  set(gensrcdict ${dictionary}Dict.cpp)

  if(ARG_SPLIT_CLASSDEF)
    set(ARG_OPTIONS ${ARG_OPTIONS} --split=classdef)
    set(gensrcclassdef ${dictionary}Dict_classdef.cpp)
  else()
    set(gensrcclassdef)
  endif()

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
    OUTPUT ${gensrcdict} ${rootmapname} ${gensrcclassdef}
    COMMAND ${ROOT_genreflex_CMD}
         ${headerfiles} -o ${gensrcdict} ${gccxmlopts} ${rootmapopts} --select=${selectionfile}
         --gccxmlpath=${GCCXML_home} ${ARG_OPTIONS} ${include_dirs} ${definitions}
    DEPENDS ${headerfiles} ${selectionfile})

  # Creating this target at ALL level enables the possibility to generate dictionaries (genreflex step)
  # well before the dependent libraries of the dictionary are build
  add_custom_target(${dictionary}Gen ALL DEPENDS ${gensrcdict} ${rootmapname} ${gensrcclassdef})

  set_property(TARGET ${dictionary}Gen PROPERTY ROOTMAPFILE ${rootmapname})
endmacro()

#-------------------------------------------------------------------------------
# reflex_dictionary(dictionary headerfile selectionfile OPTIONS opt1 opt2 ...)
#
# Generate and build a Reflex dictionary library from the specified header and selection.
#-------------------------------------------------------------------------------
function(reflex_dictionary dictionary headerfile selectionfile)
  CMAKE_PARSE_ARGUMENTS(ARG "SPLIT_CLASSDEF" "" "LINK_LIBRARIES;OPTIONS" ${ARGN})
  # ensure that we split on the spaces
  separate_arguments(ARG_OPTIONS)
  # we need to forward the SPLIT_CLASSDEF option to reflex_dictionary()
  if(ARG_SPLIT_CLASSDEF)
    set(ARG_SPLIT_CLASSDEF SPLIT_CLASSDEF)
  else()
    set(ARG_SPLIT_CLASSDEF)
  endif()
  reflex_generate_dictionary(${dictionary} ${headerfile} ${selectionfile} OPTIONS ${ARG_OPTIONS} ${ARG_SPLIT_CLASSDEF})
  include_directories(${ROOT_INCLUDE_DIR})
  add_library(${dictionary}Dict MODULE ${gensrcdict})
  _find_ROOT_components(Reflex)
  if(NOT ROOT_Reflex_LIBRARY)
    message(FATAL_ERROR "Cannot find ROOT Reflex component: cannot build dictionary ${dictionary}")
  endif()
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
