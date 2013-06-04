# - Locate pythia6 library
# Defines:
#
#  PYTHIA8_FOUND
#  PYTHIA8_INCLUDE_DIR
#  PYTHIA8_INCLUDE_DIRS (not cached)
#  PYTHIA8_LIBRARY
#  PYTHIA8_LIBRARIES (not cached)


find_path(PYTHIA8_INCLUDE_DIR Pythia.h
          HINTS $ENV{PYTHIA8_ROOT_DIR}/include ${PYTHIA8_ROOT_DIR}/include)

find_library(PYTHIA8_LIBRARY NAMES pythia8 Pythia8
             HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

find_library(PYTHIA8_hepmcinterface_LIBRARY NAMES hepmcinterface
             HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

find_library(PYTHIA8_lhapdfdummy_LIBRARY NAMES lhapdfdummy
             HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

set(PYTHIA8_INCLUDE_DIRS ${PYTHIA8_INCLUDE_DIR})
set(PYTHIA8_LIBRARIES ${PYTHIA8_LIBRARY} ${PYTHIA8_hepmcinterface_LIBRARY} ${PYTHIA8_lhapdfdummy_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set PHOTOS_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Pythia8 DEFAULT_MSG PYTHIA8_INCLUDE_DIR  PYTHIA8_LIBRARY PYTHIA8_hepmcinterface_LIBRARY PYTHIA8_lhapdfdummy_LIBRARY)

mark_as_advanced(PYTHIA8_FOUND PYTHIA8_INCLUDE_DIR PYTHIA8_LIBRARY PYTHIA8_hepmcinterface_LIBRARY PYTHIA8_lhapdfdummy_LIBRARY)
