# - Locate GSL library
# Defines:
#
#  GSL_FOUND
#  GSL_INCLUDE_DIR
#  GSL_INCLUDE_DIRS (not cached)
#  GSL_LIBRARY
#  GSL_CBLAS_LIBRARY
#  GSL_LIBRARIES (not cached)

find_path(GSL_INCLUDE_DIR /gsl/gsl_version.h
          HINTS $ENV{GSL_ROOT_DIR}/include ${GSL_ROOT_DIR}/include)
find_library(GSL_LIBRARY NAMES gsl
             HINTS $ENV{GSL_ROOT_DIR}/lib ${GSL_ROOT_DIR}/lib)
find_library(GSL_CBLAS_LIBRARY NAMES gslcblas
             HINTS $ENV{GSL_ROOT_DIR}/lib ${GSL_ROOT_DIR}/lib)

set(GSL_LIBRARIES ${GSL_LIBRARY} ${GSL_CBLAS_LIBRARY})

set(GSL_INCLUDE_DIRS ${GSL_INCLUDE_DIR})

# handle the QUIETLY and REQUIRED arguments and set GSL_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GSL DEFAULT_MSG GSL_INCLUDE_DIR GSL_LIBRARIES)

mark_as_advanced(GSL_FOUND GSL_INCLUDE_DIR GSL_LIBRARY GSL_CBLAS_LIBRARY)
