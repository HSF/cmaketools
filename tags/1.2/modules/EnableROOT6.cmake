# Internal settings for ROOT 6

# This is the list of some known component libraries
set(ROOT_ALL_COMPONENTS Core Cling RIO Hist Tree TreePlayer Matrix
                        GenVector MathCore MathMore XMLIO Graf Gui Rint Physics)
# and build tools
set(ROOT_ALL_TOOLS root rootcling genreflex)

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

# handle the QUIETLY and REQUIRED arguments and set ROOT_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ROOT DEFAULT_MSG ${_root_required_vars})
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

if(ROOT_rootcling_CMD)
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

  add_custom_command(
    OUTPUT ${gensrcdict} ${rootmapname} ${gensrcclassdef}
    COMMAND ${ROOT_genreflex_CMD}
         ${headerfiles} -o ${gensrcdict} ${rootmapopts} --select=${selectionfile}
         ${ARG_OPTIONS} ${include_dirs} ${definitions}
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
  target_link_libraries(${dictionary}Dict ${ARG_LINK_LIBRARIES} ${ROOT_Core_LIBRARY})
  # ensure that *Gen and *Dict are not built at the same time
  add_dependencies(${dictionary}Dict ${dictionary}Gen)
  # Attach the name of the rootmap file to the target so that it can be used from
  set_property(TARGET ${dictionary}Dict PROPERTY ROOTMAPFILE ${rootmapname})
endfunction()

#-------------------------------------------------------------------------------
# cling_generate_dictionary(output_file linkdef_file input_file1 [input_file2 ...])
#
# Generate and build a ROOT (Cling) dictionary C++ source from the specified linkdef and input files.
#-------------------------------------------------------------------------------
macro(cling_generate_dictionary output_file linkdef_file)
  get_directory_property(_incdirs INCLUDE_DIRECTORIES)
  foreach(d ${CMAKE_CURRENT_SOURCE_DIR} ${_incdirs})
   set(include_dirs ${include_dirs} -I${d})
  endforeach()
  get_filename_component(_output_hdr ${output_file} NAME_WE)
  set(_output_files ${output_file} ${_output_hdr}.h)
  add_custom_command(OUTPUT ${_output_files}
                     COMMAND ${ROOT_rootcling_CMD}
                             -f ${output_file} -c -DHAVE_CONFIG_H ${include_dirs} ${ARGN} ${linkdef_file}
                     DEPENDS ${ARGN} ${linkdef_file})
endmacro()
