# Special defaults
if (LCG_COMPVERS VERSION_LESS "47")
  set(GAUDI_CPP11_DEFAULT OFF)
else()
  # C++11 is enable by default on gcc >= 4.7
  set(GAUDI_CPP11_DEFAULT ON)
endif()

#--- Gaudi Build Options -------------------------------------------------------
# Build options that map to compile time features
#
option(GAUDI_V21
       "disable backward compatibility hacks (implies all G21_* options)"
       OFF)
option(G21_HIDE_SYMBOLS
       "enable explicit symbol visibility on gcc-4"
       OFF)
option(G21_NEW_INTERFACES
       "disable backward-compatibility hacks in IInterface and InterfaceID"
       OFF)
option(G21_NO_ENDREQ
       "disable the 'endreq' stream modifier (use 'endmsg' instead)"
       OFF)
option(G21_NO_DEPRECATED
       "remove deprecated methods and functions"
       OFF)
option(G22_NEW_SVCLOCATOR
       "use (only) the new interface of the ServiceLocator"
       OFF)
option(GAUDI_V22
       "enable some API extensions"
       OFF)

option(GAUDI_CMT_RELEASE
       "use CMT deafult release flags instead of the CMake ones"
       ON)

option(GAUDI_CPP11
       "enable C++11 compilation"
       ${GAUDI_CPP11_DEFAULT})


#--- Compilation Flags ---------------------------------------------------------
if(NOT GAUDI_FLAGS_SET)
  #message(STATUS "Setting cached build flags")

  if(MSVC90)

    set(CMAKE_CXX_FLAGS_DEBUG "/D_NDEBUG /MD /Zi /Ob0 /Od /RTC1"
        CACHE STRING "Flags used by the compiler during debug builds."
        FORCE)
    set(CMAKE_C_FLAGS_DEBUG "/D_NDEBUG /MD /Zi /Ob0 /Od /RTC1"
        CACHE STRING "Flags used by the compiler during debug builds."
        FORCE)

    if(GAUDI_CMT_RELEASE)
      set(CMAKE_CXX_FLAGS_RELEASE "/O2"
          CACHE STRING "Flags used by the compiler during release builds."
          FORCE)
      set(CMAKE_C_FLAGS_RELEASE "/O2"
          CACHE STRING "Flags used by the compiler during release builds."
          FORCE)
    endif()

  else()

    # Common compilation flags
    set(CMAKE_CXX_FLAGS
        "-fmessage-length=0 -pipe -ansi -Wall -Wextra -Werror=return-type -pthread -pedantic -Wwrite-strings -Wpointer-arith -Woverloaded-virtual -Wno-long-long"
        CACHE STRING "Flags used by the compiler during all build types."
        FORCE)
    set(CMAKE_C_FLAGS
        "-fmessage-length=0 -pipe -ansi -Wall -Wextra -Werror=return-type -pthread -pedantic -Wwrite-strings -Wpointer-arith -Wno-long-long"
        CACHE STRING "Flags used by the compiler during all build types."
        FORCE)
    set(CMAKE_Fortran_FLAGS
        "-fmessage-length=0 -pipe -Wall -Wextra -Werror=return-type -pthread -pedantic -fsecond-underscore"
        CACHE STRING "Flags used by the compiler during all build types."
        FORCE)

    # Build type compilation flags (if different from default or uknown to CMake)
    if(GAUDI_CMT_RELEASE)
      set(CMAKE_CXX_FLAGS_RELEASE "-O2 -DNDEBUG"
          CACHE STRING "Flags used by the compiler during release builds."
          FORCE)
      set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG"
          CACHE STRING "Flags used by the compiler during release builds."
          FORCE)
      set(CMAKE_Fortran_FLAGS_RELEASE "-O2 -DNDEBUG"
          CACHE STRING "Flags used by the compiler during release builds."
          FORCE)
    endif()

    if (CMAKE_BUILD_TYPE STREQUAL "Debug" AND LCG_COMPVERS VERSION_GREATER "47")
      # Use -Og with Debug builds in gcc >= 4.8
      set(CMAKE_CXX_FLAGS_DEBUG "-Og -g"
          CACHE STRING "Flags used by the compiler during Debug builds."
          FORCE)
      set(CMAKE_C_FLAGS_DEBUG "-Og -g"
          CACHE STRING "Flags used by the compiler during Debug builds."
          FORCE)
      set(CMAKE_C_FLAGS_DEBUG "-Og -g"
          CACHE STRING "Flags used by the compiler during Debug builds."
          FORCE)
    endif()

    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
        CACHE STRING "Flags used by the compiler during Release with Debug Info builds."
        FORCE)
    set(CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
        CACHE STRING "Flags used by the compiler during Release with Debug Info builds."
        FORCE)
    set(CMAKE_Fortran_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
        CACHE STRING "Flags used by the compiler during Release with Debug Info builds."
        FORCE)

    set(CMAKE_CXX_FLAGS_COVERAGE "--coverage"
        CACHE STRING "Flags used by the compiler during coverage builds."
        FORCE)
    set(CMAKE_C_FLAGS_COVERAGE "--coverage"
        CACHE STRING "Flags used by the compiler during coverage builds."
        FORCE)
    set(CMAKE_Fortran_FLAGS_COVERAGE "--coverage"
        CACHE STRING "Flags used by the compiler during coverage builds."
        FORCE)

    set(CMAKE_CXX_FLAGS_PROFILE "-pg"
        CACHE STRING "Flags used by the compiler during profile builds."
        FORCE)
    set(CMAKE_C_FLAGS_PROFILE "-pg"
        CACHE STRING "Flags used by the compiler during profile builds."
        FORCE)
    set(CMAKE_Fortran_FLAGS_PROFILE "-pg"
        CACHE STRING "Flags used by the compiler during profile builds."
        FORCE)


    # The others are already marked as 'advanced' by CMake, these are custom.
    mark_as_advanced(CMAKE_C_FLAGS_COVERAGE CMAKE_CXX_FLAGS_COVERAGE CMAKE_Fortran_FLAGS_COVERAGE
                     CMAKE_C_FLAGS_PROFILE CMAKE_CXX_FLAGS_PROFILE CMAKE_Fortran_FLAGS_PROFILE)
    mark_as_advanced(CMAKE_Fortran_COMPILER CMAKE_Fortran_FLAGS
                     CMAKE_Fortran_FLAGS_RELEASE CMAKE_Fortran_FLAGS_RELWITHDEBINFO)

  endif()

  #--- Link shared flags -------------------------------------------------------
  if (CMAKE_SYSTEM_NAME MATCHES Linux)
    set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--as-needed -Wl,--no-undefined  -Wl,-z,max-page-size=0x1000"
        CACHE STRING "Flags used by the linker during the creation of dll's."
        FORCE)
    set(CMAKE_MODULE_LINKER_FLAGS "-Wl,--as-needed -Wl,--no-undefined  -Wl,-z,max-page-size=0x1000"
        CACHE STRING "Flags used by the linker during the creation of modules."
        FORCE)
    set(CMAKE_EXE_LINKER_FLAGS "-Wl,--as-needed -Wl,--no-undefined  -Wl,-z,max-page-size=0x1000"
        CACHE STRING "Flags used by the linker during the creation of executables."
        FORCE)
  endif()

  if(APPLE)
    # special link options for MacOSX
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -flat_namespace -undefined dynamic_lookup"
        CACHE STRING "Flags used by the linker during the creation of dll's."
        FORCE)
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -flat_namespace -undefined dynamic_lookup"
        CACHE STRING "Flags used by the linker during the creation of modules."
        FORCE)
  endif()

  # prevent resetting of the flags
  set(GAUDI_FLAGS_SET ON
      CACHE INTERNAL "flag to check if the compilation flags have already been set")
endif()


if(UNIX)
  add_definitions(-D_GNU_SOURCE -Dunix -Df2cFortran)

  if (CMAKE_SYSTEM_NAME MATCHES Linux)
    add_definitions(-Dlinux)
  endif()
endif()

if(MSVC90)
  add_definitions(/wd4275 /wd4251 /wd4351)
  add_definitions(-DBOOST_ALL_DYN_LINK -DBOOST_ALL_NO_LIB)
  add_definitions(/nologo)
endif()

if(APPLE)
  # by default, CMake uses the option -bundle for modules, but we need -dynamiclib for them too
  string(REPLACE "-bundle" "-dynamiclib" CMAKE_SHARED_MODULE_CREATE_C_FLAGS "${CMAKE_SHARED_MODULE_CREATE_C_FLAGS}")
  string(REPLACE "-bundle" "-dynamiclib" CMAKE_SHARED_MODULE_CREATE_CXX_FLAGS "${CMAKE_SHARED_MODULE_CREATE_CXX_FLAGS}")
endif()

#--- Special build flags -------------------------------------------------------
if ((GAUDI_V21 OR G21_HIDE_SYMBOLS) AND (LCG_COMP STREQUAL gcc AND LCG_COMPVERS MATCHES "4[0-9]"))
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden -fvisibility-inlines-hidden")
endif()

if (GAUDI_CPP11)
  if (LCG_COMPVERS VERSION_LESS "47")
    # gcc 4.6 only understands c++0x
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
  else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c11")
  endif()
endif()

if(NOT GAUDI_V21)
  if(GAUDI_V22)
    add_definitions(-DGAUDI_V22_API)
  else()
    add_definitions(-DGAUDI_V20_COMPAT)
  endif()
  # special case
  if(G21_HIDE_SYMBOLS AND (comp MATCHES gcc4))
    add_definitions(-DG21_HIDE_SYMBOLS)
  endif()
  #
  foreach (feature G21_NEW_INTERFACES G21_NO_ENDREQ G21_NO_DEPRECATED G22_NEW_SVCLOCATOR)
    if (${feature})
      add_definitions(-D${feature})
    endif()
  endforeach()
endif()

if (LCG_HOST_ARCH AND LCG_ARCH)
  # this is valid only in the LCG toolchain context
  if (LCG_HOST_ARCH STREQUAL x86_64 AND LCG_ARCH STREQUAL i686)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m32")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m32")
    set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -m32")
    set(GCCXML_CXX_FLAGS "${GCCXML_CXX_FLAGS} -m32")
  elseif(NOT LCG_HOST_ARCH STREQUAL LCG_ARCH)
    message(FATAL_ERROR "Cannot build for ${LCG_ARCH} on ${LCG_HOST_ARCH}.")
  endif()
endif()

#--- Tuning of warnings --------------------------------------------------------
if(GAUDI_HIDE_WARNINGS)
  if(LCG_COMP MATCHES clang)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-overloaded-virtual -Wno-char-subscripts -Wno-unused-parameter")
  elseif(LCG_COMP STREQUAL gcc AND LCG_COMPVERS MATCHES "4[3-9]|max")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated -Wno-empty-body")
    if(LCG_COMPVERS MATCHES "48|max")
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-unused-local-typedefs")
    endif()
  endif()
endif()

#--- Special flags -------------------------------------------------------------
# FIXME: enforce the use of Boost Filesystem V3 to be compatible between 1.44 and 1.48
add_definitions(-DBOOST_FILESYSTEM_VERSION=3)
# FIXME: enforce the use of Boost Phoenix V3 (V2 does not work with recent compilers)
#        see http://stackoverflow.com/q/20721486
#        and http://stackoverflow.com/a/20440238/504346
add_definitions(-DBOOST_SPIRIT_USE_PHOENIX_V3)

if((LCG_COMP STREQUAL gcc AND LCG_COMPVERS MATCHES "47|max") OR GAUDI_CPP11)
  set(GCCXML_CXX_FLAGS "${GCCXML_CXX_FLAGS} -D__STRICT_ANSI__")
endif()

if(LCG_COMP STREQUAL gcc AND LCG_COMPVERS STREQUAL 43)
  # The -pedantic flag gives problems on GCC 4.3.
  string(REPLACE "-pedantic" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
  string(REPLACE "-pedantic" "" CMAKE_C_FLAGS   "${CMAKE_C_FLAGS}")
endif()

if(GAUDI_ATLAS)
  # FIXME: this macro is used in ATLAS to simplify the migration to Gaudi v25,
  #        unfortunately it's not possible to detect the version of Gaudi at this point
  #        so we assume that any CMake-based build in ATLAS uses Gaudi >= v25
  add_definitions(-DHAVE_GAUDI_PLUGINSVC)
  
  add_definitions(-DATLAS_GAUDI_V21)
  include(AthenaBuildFlags OPTIONAL)
endif()
