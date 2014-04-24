# - Try to find ThePEG
# Defines:
#
#  THEPEG_FOUND
#  THEPEG_INCLUDE_DIR
#  THEPEG_INCLUDE_DIRS (not cached)
#  THEPEG_LIBRARY
#  THEPEG_LIBRARIES (not cached)
#  THEPEG_LIBRARY_DIRS (not cached)

find_path(THEPEG_INCLUDE_DIR ThePEG/Config/ThePEG.h
          HINTS $ENV{THEPEG_ROOT_DIR}/include ${THEPEG_ROOT_DIR}/include)

find_library(THEPEG_LIBRARY NAMES ThePEG
             HINTS $ENV{THEPEG_ROOT_DIR}/lib ${THEPEG_ROOT_DIR}/lib
             PATH_SUFFIXES ThePEG)

mark_as_advanced(THEPEG_INCLUDE_DIR THEPEG_LIBRARY)

# handle the QUIETLY and REQUIRED arguments and set ThePEG_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ThePEG DEFAULT_MSG THEPEG_INCLUDE_DIR THEPEG_LIBRARY)

mark_as_advanced(THEPEG_FOUND)

set(THEPEG_LIBRARIES ${THEPEG_LIBRARY})
get_filename_component(THEPEG_LIBRARY_DIRS ${THEPEG_LIBRARY} PATH)

set(THEPEG_INCLUDE_DIRS ${THEPEG_INCLUDE_DIR})
