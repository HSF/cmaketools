# - Locate herwig libraries and includes
# Defines:
#
#  HERWIG_FOUND
#  HERWIG_INCLUDE_DIR
#  HERWIG_INCLUDE_DIRS (not cached)
#  HERWIG_LIBRARY
#  HERWIG_LIBRARY_DIR (not cached)
#  HERWIG_LIBRARIES (not cached)


find_path(HERWIG_INCLUDE_DIR HERWIG65.INC
          HINTS $ENV{HERWIG_ROOT_DIR}/include ${HERWIG_ROOT_DIR}/include)

find_library(HERWIG_LIBRARY NAMES herwig Herwig
             HINTS $ENV{HERWIG_ROOT_DIR}/lib ${HERWIG_ROOT_DIR}/lib)

find_library(HERWIG_dummy_LIBRARY NAMES herwig_dummy Herwig_dummy
             HINTS $ENV{HERWIG_ROOT_DIR}/lib ${HERWIG_ROOT_DIR}/lib)

find_library(HERWIG_pdfdummy_LIBRARY NAMES herwig_pdfdummy Herwig_pdfdummy
             HINTS $ENV{HERWIG_ROOT_DIR}/lib ${HERWIG_ROOT_DIR}/lib)


set(HERWIG_INCLUDE_DIRS ${HERWIG_INCLUDE_DIR})
set(HERWIG_LIBRARIES ${HERWIG_LIBRARY} ${HERWIG_dummy_LIBRARY} ${HERWIG_pdfdummy_LIBRARY})
get_filename_component(HERWIG_LIBRARY_DIR ${HERWIG_LIBRARY} PATH)

# handle the QUIETLY and REQUIRED arguments and set HERWIG_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Herwig DEFAULT_MSG HERWIG_INCLUDE_DIR  HERWIG_LIBRARY HERWIG_dummy_LIBRARY HERWIG_pdfdummy_LIBRARY)

mark_as_advanced(HERWIG_FOUND HERWIG_INCLUDE_DIR HERWIG_LIBRARY HERWIG_dummy_LIBRARY HERWIG_pdfdummy_LIBRARY)
