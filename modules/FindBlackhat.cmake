# - Locate Blackhat libraries
# Defines:
#
#  BLACKHAT_FOUND
#  BLACKHAT_INCLUDE_DIR
#  BLACKHAT_LIBRARIES

find_path(BLACKHAT_INCLUDE_DIR blackhat/BH_interface.h
          HINTS $ENV{BLACKHAT_ROOT_DIR}/include ${BLACKHAT_ROOT_DIR}/include)
find_path(BLACKHAT_BIN_DIR blackhat-config
          HINTS $ENV{BLACKHAT_ROOT_DIR}/bin ${BLACKHAT_ROOT_DIR}/bin)

set(BLACKHAT_INCLUDE_DIRS ${BLACKHAT_INCLUDE_DIR})

#Compose library list from the output of blackhat-config:

execute_process(COMMAND ${BLACKHAT_BIN_DIR}/blackhat-config --libs OUTPUT_VARIABLE bliblist0)
string(REGEX MATCHALL "-l[A-Za-z0-9_-]+" bliblist0 "${bliblist0}")
list(REMOVE_ITEM bliblist0 "-lqd")
set(BLACKHAT_LIBRARIES "")
foreach(_c ${bliblist0})
  string(REPLACE "-l" "" _c ${_c})
  find_library(libi NAMES ${_c}
               HINTS $ENV{BLACKHAT_ROOT_DIR}/lib/blackhat ${BLACKHAT_ROOT_DIR}/lib/blackhat)
  list(APPEND BLACKHAT_LIBRARIES "${libi}")
  unset(libi CACHE)
endforeach()
message(STATUS "blackhat libraries list for linking: ${BLACKHAT_LIBRARIES}")

# handle the QUIETLY and REQUIRED arguments and set BLACKHAT_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Blackhat DEFAULT_MSG BLACKHAT_INCLUDE_DIR BLACKHAT_BIN_DIR BLACKHAT_LIBRARIES)
mark_as_advanced(BLACKHAT_FOUND BLACKHAT_INCLUDE_DIR BLACKHAT_BIN_DIR BLACKHAT_LIBRARIES)
