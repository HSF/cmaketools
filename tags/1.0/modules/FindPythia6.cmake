# - Locate pythia6 library
# Defines:
#
#  PYTHIA6_FOUND
#  PYTHIA6_INCLUDE_DIR
#  PYTHIA6_INCLUDE_DIRS (not cached)
#  PYTHIA6_LIBRARY
#  PYTHIA6_LIBRARY_DIR (not cached)
#  PYTHIA6_LIBRARIES (not cached)


find_path(PYTHIA6_INCLUDE_DIR general_pythia.inc
          HINTS $ENV{PYTHIA6_ROOT_DIR}/include ${PYTHIA6_ROOT_DIR}/include)

find_library(PYTHIA6_LIBRARY NAMES pythia6 Pythia6
             HINTS $ENV{PYTHIA6_ROOT_DIR}/lib ${PYTHIA6_ROOT_DIR}/lib)

find_library(PYTHIA6_dummy_LIBRARY NAMES pythia6_dummy Pythia6_dummy
             HINTS $ENV{PYTHIA6_ROOT_DIR}/lib ${PYTHIA6_ROOT_DIR}/lib)

find_library(PYTHIA6_pdfdummy_LIBRARY NAMES pythia6_pdfdummy Pythia6_pdfdummy
             HINTS $ENV{PYTHIA6_ROOT_DIR}/lib ${PYTHIA6_ROOT_DIR}/lib)


set(PYTHIA6_INCLUDE_DIRS ${PYTHIA6_INCLUDE_DIR})
set(PYTHIA6_LIBRARIES ${PYTHIA6_LIBRARY} ${PYTHIA6_dummy_LIBRARY} ${PYTHIA6_pdfdummy_LIBRARY})
get_filename_component(PYTHIA6_LIBRARY_DIR ${PYTHIA6_LIBRARY} PATH)

# handle the QUIETLY and REQUIRED arguments and set PHOTOS_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Pythia6 DEFAULT_MSG PYTHIA6_INCLUDE_DIR  PYTHIA6_LIBRARY PYTHIA6_dummy_LIBRARY PYTHIA6_pdfdummy_LIBRARY)

mark_as_advanced(PYTHIA6_FOUND PYTHIA6_INCLUDE_DIR PYTHIA6_LIBRARY PYTHIA6_dummy_LIBRARY PYTHIA6_pdfdummy_LIBRARY)
