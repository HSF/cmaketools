################################################################################
# HEP CMake toolchain
#-------------------------------------------------------------------------------
# The HEP CMake toolchain is required to build a project using the libraries and
# tools provided by SPI/SFT (a.k.a. LCGCMT).
#
# The variables used to tune the toolchain behavior are:
#
#  - BINARY_TAG: inferred from the system or from the environment (CMAKECONFIG,
#                CMTCONFIG), defines the target platform (by default is the same
#                as the host)
#  - LCG_SYSTEM: by default it is derived from BINARY_TAG, but it can be set
#                explicitly to a compatible supported platform if the default
#                one is not supported.
#                E.g.: if BINARY_TAG is x86_64-ubuntu12.04-gcc46-opt, LCG_SYSTEM
#                      should be set to x86_64-slc6-gcc46.
################################################################################

################################################################################
# Functions to get system informations for the LCG configuration.
################################################################################
# Get the host architecture.
function(lcg_find_host_arch)
  if(NOT LCG_HOST_ARCH)
    if(CMAKE_HOST_SYSTEM_PROCESSOR)
      set(arch ${CMAKE_HOST_SYSTEM_PROCESSOR})
    else()
      if(UNIX)
        execute_process(COMMAND uname -p OUTPUT_VARIABLE arch OUTPUT_STRIP_TRAILING_WHITESPACE)
      else()
        set(arch $ENV{PROCESSOR_ARCHITECTURE})
      endif()
    endif()

    set(LCG_HOST_ARCH ${arch} CACHE STRING "Architecture of the host (same as CMAKE_HOST_SYSTEM_PROCESSOR).")
    mark_as_advanced(LCG_HOST_ARCH)
  endif()
endfunction()
################################################################################
# Detect the OS name and version
function(lcg_find_host_os)
  if(NOT LCG_HOST_OS OR NOT LCG_HOST_OSVERS)
    if(APPLE)
      set(os mac)
      execute_process(COMMAND sw_vers "-productVersion"
                      COMMAND cut -d . -f 1-2
                      OUTPUT_VARIABLE osvers OUTPUT_STRIP_TRAILING_WHITESPACE)
      string(REPLACE "." "" osvers ${osvers})
    elseif(WIN32)
      set(os winxp)
      set(osvers)
    else()
      execute_process(COMMAND cat /etc/issue OUTPUT_VARIABLE issue OUTPUT_STRIP_TRAILING_WHITESPACE)
      if(issue MATCHES Ubuntu)
        set(os ubuntu)
        string(REGEX REPLACE ".*Ubuntu ([0-9]+)[.]([0-9]+).*" "\\1.\\2" osvers "${issue}")
      elseif(issue MATCHES SLC)
        set(os slc)
        string(REGEX REPLACE ".*release ([0-9]+)[.].*" "\\1" osvers "${issue}")
      else()
        set(os linux)
        set(osvers)
      endif()
    endif()

    set(LCG_HOST_OS ${os} CACHE STRING "Name of the operating system (or Linux distribution)." FORCE)
    set(LCG_HOST_OSVERS ${osvers} CACHE STRING "Version of the operating system (or Linux distribution)." FORCE)
    mark_as_advanced(LCG_HOST_OS LCG_HOST_OSVERS)
  endif()
endfunction()
################################################################################
# Get system compiler.
function(lcg_find_host_compiler)
  if(NOT LCG_HOST_COMP OR NOT LCG_HOST_COMPVERS)
    if(WIN32)
      find_program(guessed_compiler cl gcc)
    else()
      find_program(guessed_compiler gcc icc)
    endif()
    mark_as_advanced(guessed_compiler)
    if(guessed_compiler MATCHES /cl)
      set(compiler vc)
      execute_process(COMMAND ${guessed_compiler} ERROR_VARIABLE versioninfo OUTPUT_VARIABLE out)
      string(REGEX REPLACE ".*Version ([0-9]+)[.].*" "\\1" cvers "${versioninfo}")
      math(EXPR cvers "${cvers} - 6")
    elseif(guessed_compiler MATCHES /gcc)
      set(compiler gcc)
      execute_process(COMMAND ${guessed_compiler} -dumpversion OUTPUT_VARIABLE GCC_VERSION)
      string(REGEX MATCHALL "[0-9]+" GCC_VERSION_COMPONENTS ${GCC_VERSION})
      list(GET GCC_VERSION_COMPONENTS 0 GCC_MAJOR)
      list(GET GCC_VERSION_COMPONENTS 1 GCC_MINOR)
      set(cvers ${GCC_MAJOR}${GCC_MINOR})
    else()
      set(compiler)
      set(cvers)
    endif()

    set(LCG_HOST_COMP ${compiler} CACHE STRING "Name of the host default compiler." FORCE)
    set(LCG_HOST_COMPVERS ${cvers} CACHE STRING "Version of the host default compiler." FORCE)
    mark_as_advanced(LCG_HOST_COMP LCG_HOST_COMPVERS)
  endif()
endfunction()
################################################################################
# Detect host system
function(lcg_detect_host_platform)
  lcg_find_host_arch()
  lcg_find_host_os()
  lcg_find_host_compiler()
  set(LCG_HOST_SYSTEM ${LCG_HOST_ARCH}-${LCG_HOST_OS}${LCG_HOST_OSVERS}-${LCG_HOST_COMP}${LCG_HOST_COMPVERS}
      CACHE STRING "Platform id of the system.")
  mark_as_advanced(LCG_HOST_SYSTEM)
endfunction()
################################################################################
# Get the target system platform (arch., OS, compiler)
function(lcg_get_target_platform)
  if(NOT BINARY_TAG)
    # Take the target system id from the environment
    if(NOT "$ENV{CMAKECONFIG}" STREQUAL "")
      set(tag $ENV{CMAKECONFIG})
      set(tag_source CMAKECONFIG)
    elseif(NOT "$ENV{CMTCONFIG}" STREQUAL "")
      set(tag $ENV{CMTCONFIG})
      set(tag_source CMTCONFIG)
    else()
      set(tag ${LCG_HOST_SYSTEM}-opt)
      set(tag_source default)
    endif()
    message(STATUS "Target binary tag from ${tag_source}: ${tag}")
    set(BINARY_TAG ${tag} CACHE STRING "Platform id for the produced binaries.")
  endif()
  # Split the target binary tag
  string(REGEX MATCHALL "[^-]+" out ${BINARY_TAG})
  list(GET out 0 arch)
  list(GET out 1 os)
  list(GET out 2 comp)
  list(GET out 3 type)

  set(LCG_BUILD_TYPE ${type} CACHE STRING "Type of build (LCG id).")

  set(LCG_TARGET ${arch}-${os}-${comp})
  if(NOT LCG_SYSTEM)
    set(LCG_SYSTEM ${arch}-${os}-${comp} CACHE STRING "Platform id of the target system or a compatible one.")
  endif()

  # Convert the components of the tag in the equivalents of LCG_HOST_*,
  # but transient
  set(LCG_ARCH  ${arch})

  if (os MATCHES "([^0-9.]+)([0-9.]+)")
    set(LCG_OS     ${CMAKE_MATCH_1})
    set(LCG_OSVERS ${CMAKE_MATCH_2})
  else()
    set(LCG_OS     ${os})
    set(LCG_OSVERS "")
  endif()

  if (comp MATCHES "([^0-9.]+)([0-9.]+|max)")
    set(LCG_COMP     ${CMAKE_MATCH_1})
    set(LCG_COMPVERS ${CMAKE_MATCH_2})
  else()
    set(LCG_COMP     ${comp})
    set(LCG_COMPVERS "")
  endif()

  # Convert LCG_BUILD_TYPE to CMAKE_BUILD_TYPE
  if(LCG_BUILD_TYPE STREQUAL "opt")
    set(type Release)
  elseif(LCG_BUILD_TYPE STREQUAL "dbg")
    set(type Debug)
  elseif(LCG_BUILD_TYPE STREQUAL "cov")
    set(type Coverage)
  else()
    message(FATAL_ERROR "LCG build type ${type} not supported.")
  endif()
  set(CMAKE_BUILD_TYPE ${type} CACHE STRING
      "Choose the type of build, options are: None Debug Release Coverage Profile RelWithDebInfo MinSizeRel.")

  # architecture
  set(CMAKE_SYSTEM_PROCESSOR ${LCG_ARCH} PARENT_SCOPE)

  # system name
  if(LCG_OS STREQUAL "winxp")
    set(CMAKE_SYSTEM_NAME Windows PARENT_SCOPE)
  elseif(LCG_OS STREQUAL "mac")
    set(CMAKE_SYSTEM_NAME Darwin PARENT_SCOPE)
  elseif(LCG_OS STREQUAL "slc" OR LCG_OS STREQUAL "ubuntu")
    set(CMAKE_SYSTEM_NAME Linux PARENT_SCOPE)
  else()
    message(FATAL_ERROR "OS ${LCG_OS} is not supported.")
  endif()

  # set default platform ids
  set(LCG_platform ${LCG_SYSTEM}-${LCG_BUILD_TYPE} CACHE STRING "Platform ID for the AA project binaries.")
  set(LCG_system   ${LCG_SYSTEM}-opt               CACHE STRING "Platform ID for the external libraries.")

  mark_as_advanced(LCG_platform LCG_system)

  # Report the platform ids.
  message(STATUS "Target system: ${LCG_TARGET}")
  message(STATUS "Build type: ${LCG_BUILD_TYPE}")

  if(NOT LCG_HOST_SYSTEM STREQUAL LCG_TARGET)
    message(STATUS "Host system: ${LCG_HOST_SYSTEM}")
  endif()

  if(NOT LCG_TARGET STREQUAL LCG_SYSTEM)
    message(STATUS "Use LCG system: ${LCG_SYSTEM}")
  endif()

  # copy variables to parent scope
  foreach(v ARCH OS OSVERS COMP COMPVERS TARGET)
    set(LCG_${v} ${LCG_${v}} PARENT_SCOPE)
  endforeach()
endfunction()


################################################################################
# Run platform detection (system and target).
################################################################################
# Deduce the LCG configuration tag from the system
lcg_detect_host_platform()
lcg_get_target_platform()

## Debug messages.
#foreach(p LCG_HOST_ LCG_)
#  foreach(v ARCH OS OSVERS COMP COMPVERS)
#    message(STATUS "toolchain: ${p}${v} -> ${${p}${v}}")
#  endforeach()
#endforeach()
#message(STATUS "toolchain: LCG_BUILD_TYPE -> ${LCG_BUILD_TYPE}")
#
#message(STATUS "toolchain: CMAKE_HOST_SYSTEM_PROCESSOR -> ${CMAKE_HOST_SYSTEM_PROCESSOR}")
#message(STATUS "toolchain: CMAKE_HOST_SYSTEM_NAME      -> ${CMAKE_HOST_SYSTEM_NAME}")
#message(STATUS "toolchain: CMAKE_HOST_SYSTEM_VERSION   -> ${CMAKE_HOST_SYSTEM_VERSION}")

# LCG location
if(NOT heptools_version)
  message(FATAL_ERROR "Variable heptools_version not defined. It must be defined before including heptools-common.cmake")
endif()

find_path(LCG_releases NAMES LCGCMT/LCGCMT_${heptools_version} LCGCMT/LCGCMT-${heptools_version} PATHS ENV CMTPROJECTPATH)
if(LCG_releases)
  message(STATUS "Found LCGCMT ${heptools_version} in ${LCG_releases}")
else()
  message(FATAL_ERROR "Cannot find location of LCGCMT ${heptools_version}")
endif()
# define location of externals
get_filename_component(_lcg_rel_type ${LCG_releases} NAME)
if(_lcg_rel_type STREQUAL "external")
  set(LCG_external ${LCG_releases})
else()
  get_filename_component(LCG_external ${LCG_releases}/../../external ABSOLUTE)
endif()

# Define the variables and search paths for AA projects
macro(LCG_AA_project name version)
  set(${name}_config_version ${version})
  set(${name}_native_version ${version})
  set(${name}_base ${LCG_releases}/${name}/${${name}_native_version})
  set(${name}_home ${${name}_base}/${LCG_platform})
  if(${name} STREQUAL ROOT)
    # ROOT is special
    set(ROOT_home ${ROOT_home}/root)
  endif()
  list(APPEND LCG_projects ${name})
endmacro()

# Define variables and location of the compiler.
macro(LCG_compiler id flavor version)
  if(${id} STREQUAL ${LCG_COMP}${LCG_COMPVERS})
    if(${flavor} STREQUAL "gcc")
      set(compiler_root ${LCG_external}/${flavor}/${version}/${LCG_HOST_ARCH}-${LCG_HOST_OS}${LCG_HOST_OSVERS})
      set(c_compiler_names lcg-gcc-${version})
      set(cxx_compiler_names lcg-g++-${version})
    elseif(${flavor} STREQUAL "icc")
      # Note: icc must be in the path already because of the licensing
      set(compiler_root)
      set(c_compiler_names lcg-icc-${version} icc)
      set(cxx_compiler_names lcg-icpc-${version} icpc)
    elseif(${flavor} STREQUAL "clang")
      set(compiler_root ${LCG_external}/llvm/${version}/${LCG_HOST_ARCH}-${LCG_HOST_OS}${LCG_HOST_OSVERS})
      set(c_compiler_names lcg-clang-${version} clang)
      set(cxx_compiler_names lcg-clang++-${version} clang++)
    else()
      message(FATAL_ERROR "Uknown compiler flavor ${flavor}.")
    endif()
    #message(STATUS "LCG_compiler($ARGV) -> ${c_compiler_name} ${cxx_compiler_name} ${compiler_root}")
    # We need to unset the default compiler names to make find_program() work.
    find_program(CMAKE_C_COMPILER
                 NAMES ${c_compiler_names}
                 PATHS ${compiler_root}/bin)
    find_program(CMAKE_CXX_COMPILER
                 NAMES ${cxx_compiler_names}
                 PATHS ${compiler_root}/bin)
    #message(STATUS "LCG_compiler($ARGV) -> ${CMAKE_C_COMPILER} ${CMAKE_CXX_COMPILER}")
  endif()
endmacro()

# Define the variables for external projects
# Usage:
#   LCG_external_package(<Package> <version> [<directory name>])
# Examples:
#   LCG_external_package(Boost 1.44.0)
#   LCG_external_package(CLHEP 1.9.4.7 clhep)
macro(LCG_external_package name version)
  set(${name}_config_version ${version})
  set(${name}_native_version ${version})
  if(${ARGC} GREATER 2)
    set(${name}_directory_name ${ARGV2})
  else()
    set(${name}_directory_name ${name})
  endif()
  list(APPEND LCG_externals ${name})
endmacro()

# Define the search paths from the configured versions
macro(LCG_prepare_paths)
  #===============================================================================
  # Derived variables
  #===============================================================================
  string(REGEX MATCH "[0-9]+\\.[0-9]+" Python_config_version_twodigit ${Python_config_version})
  set(Python_ADDITIONAL_VERSIONS ${Python_config_version_twodigit})

  # Note: this is needed because FindBoost.cmake requires both if the patch version is 0.
  string(REGEX MATCH "[0-9]+\\.[0-9]+" Boost_config_version_twodigit ${Boost_config_version})
  set(Boost_ADDITIONAL_VERSIONS ${Boost_config_version} ${Boost_config_version_twodigit})

  #===============================================================================
  # Special cases that require a special treatment
  #===============================================================================
  if(NOT APPLE)
    # FIXME: this should be automatic... see FindBoost.cmake documentation
    # Get Boost compiler id from LCG_system
    string(REGEX MATCHALL "[^-]+" out ${LCG_SYSTEM})
    list(GET out 2 syscomp)
    set(Boost_COMPILER -${syscomp})
    #message(STATUS "Boost compiler: ${LCG_SYSTEM} -> ${syscomp}")
  endif()
  set(Boost_NO_BOOST_CMAKE ON)
  set(Boost_NO_SYSTEM_PATHS ON)

  # These externals require the version of python appended to their version.
  foreach(external Boost pytools pygraphics pyanalysis QMtest)
    if(${external}_config_version)
      set(${external}_native_version ${${external}_config_version}_python${Python_config_version_twodigit})
    endif()
  endforeach()

  # Required if both Qt3 and Qt4 are available.
  string(REGEX MATCH "[0-9]+" _qt_major_version ${Qt_config_version})
  set(DESIRED_QT_VERSION ${_qt_major_version} CACHE STRING "Pick a version of QT to use: 3 or 4")

  if(comp STREQUAL clang30)
    set(GCCXML_CXX_COMPILER gcc CACHE STRING "Compiler that GCCXML must use.")
  endif()

  # This is not really needed because Xerces has its own version macro, but it was
  # added at some point, so it is kept for backward compatibility.
  #add_definitions(-DXERCESC_GE_31)

  #===============================================================================
  # Construct the actual PREFIX and INCLUDE PATHs
  #===============================================================================
  # Define the _home variables (not cached)
  foreach(name ${LCG_externals})
    set(${name}_home ${LCG_external}/${${name}_directory_name}/${${name}_native_version}/${LCG_system})
  endforeach()

  foreach(name ${LCG_projects})
    list(APPEND LCG_PREFIX_PATH ${${name}_home})
    # We need to add python to the include path because it's the only
    # way to search for a (generic) file.
    list(APPEND LCG_INCLUDE_PATH ${${name}_base}/include ${${name}_home}/python)
  endforeach()
  # Add the LCG externals dirs to the search paths.
  foreach(name ${LCG_externals})
    list(APPEND LCG_PREFIX_PATH ${${name}_home})
  endforeach()

  # AIDA is special
  list(APPEND LCG_INCLUDE_PATH ${LCG_external}/${AIDA_directory_name}/${AIDA_native_version}/share/src/cpp)

  set(CMAKE_PREFIX_PATH ${LCG_PREFIX_PATH} ${CMAKE_PREFIX_PATH})
  set(CMAKE_INCLUDE_PATH ${LCG_INCLUDE_PATH} ${CMAKE_INCLUDE_PATH})

  #message(STATUS "LCG_PREFIX_PATH: ${LCG_PREFIX_PATH}")
endmacro()
