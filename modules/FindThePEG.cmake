# - Locate ThePEG library
# Defines:
#
#  THEPEG_FOUND
#  THEPEG_INCLUDE_DIR
#  THEPEG_LIBRARY
#  THEPEG_INCLUDE_DIRS (not cached)
#  THEPEG_LIBRARIES (not cached)

find_path(THEPEG_INCLUDE_DIR ThePEG/Config/ThePEG.h
          HINTS $ENV{THEPEG_ROOT_DIR}/include ${THEPEG_ROOT_DIR}/include)

find_library(THEPEG_LIBRARY NAMES ThePEG
             HINTS $ENV{THEPEG_ROOT_DIR}/lib/ThePEG ${THEPEG_ROOT_DIR}/lib/ThePEG)

set(THEPEG_INCLUDE_DIRS ${THEPEG_INCLUDE_DIR})
set(THEPEG_LIBRARIES ${THEPEG_LIBRARY})


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Thepeg DEFAULT_MSG THEPEG_INCLUDE_DIR THEPEG_LIBRARY)
mark_as_advanced(THEPEG_FOUND THEPEG_INCLUDE_DIR THEPEG_LIBRARY)
