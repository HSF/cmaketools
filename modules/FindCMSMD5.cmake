# - Locate MD5 library
# Defines:
#
#  MD5_FOUND
#  MD5_INCLUDE_DIR
#  MD5_INCLUDE_DIRS (not cached)
#  MD5_LIBRARY
#  MD5_CBLAS_LIBRARY
#  MD5_LIBRARIES (not cached)

find_path(MD5_INCLUDE_DIR md5.h
          HINTS $ENV{MD5ROOT}/include ${MD5ROOT}/include)
find_library(MD5_LIBRARY NAMES cms-md5
             HINTS $ENV{MD5ROOT}/lib ${MD5ROOT}/lib)

set(MD5_LIBRARIES ${MD5_LIBRARY})

set(MD5_INCLUDE_DIRS ${MD5_INCLUDE_DIR})

# handle the QUIETLY and REQUIRED arguments and set MD5_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(MD5 DEFAULT_MSG MD5_INCLUDE_DIR MD5_LIBRARIES)

mark_as_advanced(MD5_FOUND MD5_INCLUDE_DIR MD5_LIBRARY)
