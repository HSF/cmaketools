# - Locate photos library
# Defines:
#
#  PHOTOS_FOUND
#  PHOTOS_INCLUDE_DIR
#  PHOTOS_INCLUDE_DIRS (not cached)
#  PHOTOS_LIBRARY
#  PHOTOS_LIBRARIES (not cached)


find_path(PHOTOS_INCLUDE_DIR hepevt_inpphotos.inc
          HINTS $ENV{PHOTOS_ROOT_DIR}/include ${PHOTOS_ROOT_DIR}/include)

find_library(PHOTOS_LIBRARY NAMES photos
             HINTS $ENV{PHOTOS_ROOT_DIR}/lib ${PHOTOS_ROOT_DIR}/lib)

set(PHOTOS_INCLUDE_DIRS ${PHOTOS_INCLUDE_DIR})
set(PHOTOS_LIBRARIES ${PHOTOS_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set PHOTOS_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(photos DEFAULT_MSG PHOTOS_INCLUDE_DIR PHOTOS_LIBRARY)

mark_as_advanced(PHOTOS_FOUND PHOTOS_INCLUDE_DIR PHOTOS_LIBRARY)
