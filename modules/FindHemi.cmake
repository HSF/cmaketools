# - Locate Hemi library
# Defines:
#
#  HEMI_FOUND
#  HEMI_INCLUDE_DIR
#  HEMI_INCLUDE_DIRS (not cached)

find_path(HEMI_INCLUDE_DIR hemi/hemi.h
          HINTS $ENV{HEMI_ROOT_DIR} ${HEMI_ROOT_DIR})

set(HEMI_INCLUDE_DIRS ${HEMI_INCLUDE_DIR})

# handle the QUIETLY and REQUIRED arguments and set HEMI_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(HEMI DEFAULT_MSG HEMI_INCLUDE_DIR)

mark_as_advanced(HEMI_FOUND HEMI_INCLUDE_DIR)