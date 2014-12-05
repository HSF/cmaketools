# - Locate LFC library
# Defines:
#
#  LFC_FOUND
#  LFC_INCLUDE_DIR
#  LFC_INCLUDE_DIRS (not cached)
#  LFC_LIBRARIES
#  LFC_LIBRARY_DIRS (not cached)

find_path(LFC_INCLUDE_DIR lfc/lfc_api.h)
find_library(LFC_LIBRARIES NAMES lfc PATH_SUFFIXES lib64)

set(LFC_INCLUDE_DIRS ${LFC_INCLUDE_DIR})
get_filename_component(LFC_LIBRARY_DIRS ${LFC_LIBRARIES} PATH)

# handle the QUIETLY and REQUIRED arguments and set LFC_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LFC DEFAULT_MSG LFC_INCLUDE_DIR LFC_LIBRARIES)

mark_as_advanced(LFC_FOUND LFC_INCLUDE_DIR LFC_LIBRARIES)
