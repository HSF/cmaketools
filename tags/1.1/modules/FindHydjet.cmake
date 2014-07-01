# - Locate hydjet library
# Defines:
#
#  HYDJET_FOUND
#  HYDJET_INCLUDE_DIR
#  HYDJET_INCLUDE_DIRS (not cached)
#  HYDJET_LIBRARY
#  HYDJET_LIBRARIES (not cached)


set(HYDJET_INCLUDE_DIR ${HYDJET_ROOT_DIR})

find_library(HYDJET_LIBRARY NAMES hydjet
             HINTS $ENV{HYDJET_ROOT_DIR}/lib ${HYDJET_ROOT_DIR}/lib)

find_library(HYDJET_jetset73_LIBRARY NAMES jetset73hydjet
             HINTS $ENV{HYDJET_ROOT_DIR}/lib ${HYDJET_ROOT_DIR}/lib)

set(HYDJET_INCLUDE_DIRS ${HYDJET_INCLUDE_DIR})
set(HYDJET_LIBRARIES ${HYDJET_LIBRARY} ${HYDJET_jetset73_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set HYDJET_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(hydjet DEFAULT_MSG HYDJET_LIBRARY HYDJET_jetset73_LIBRARY HYDJET_INCLUDE_DIR)

mark_as_advanced(HYDJET_FOUND HYDJET_LIBRARY HYDJET_jetset73_LIBRARY HYDJET_INCLUDE_DIR)