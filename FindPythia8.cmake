# - Locate pythia6 library
# Defines:
#
#  PYTHIA8_FOUND
#  PYTHIA8_VERSION
#  PYTHIA8_INCLUDE_DIR
#  PYTHIA8_INCLUDE_DIRS (not cached)
#  PYTHIA8_LIBRARY
#  PYTHIA8_hepmcinterface_LIBRARY
#  PYTHIA8_lhapdfdummy_LIBRARY
#  PYTHIA8_LIBRARIES (not cached) : includes 3 libraries above; not to be used if lhapdf is used


find_path(PYTHIA8_INCLUDE_DIR Pythia.h Pythia8/Pythia.h
          HINTS $ENV{PYTHIA8_ROOT_DIR}/include ${PYTHIA8_ROOT_DIR}/include)

file(READ ${PYTHIA8_INCLUDE_DIR}/../xmldoc/Version.xml versionstr)
string(REGEX REPLACE ".*Pythia:versionNumber.*default.*[0-9][.]([0-9]+).*" "\\1" PYTHIA8_VERSION "${versionstr}")

find_library(PYTHIA8_LIBRARY NAMES pythia8 Pythia8
             HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

find_library(PYTHIA8_hepmcinterface_LIBRARY NAMES hepmcinterface pythia8tohepmc
               HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

find_library(PYTHIA8_lhapdfdummy_LIBRARY NAMES lhapdfdummy
             HINTS $ENV{PYTHIA8_ROOT_DIR}/lib ${PYTHIA8_ROOT_DIR}/lib)

set(PYTHIA8_INCLUDE_DIRS ${PYTHIA8_INCLUDE_DIR} ${PYTHIA8_INCLUDE_DIR}/Pythia8 )
set(PYTHIA8_LIBRARIES ${PYTHIA8_LIBRARY} ${PYTHIA8_hepmcinterface_LIBRARY} ${PYTHIA8_lhapdfdummy_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set PYTHIA8_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Pythia8 DEFAULT_MSG PYTHIA8_INCLUDE_DIR PYTHIA8_LIBRARY PYTHIA8_hepmcinterface_LIBRARY PYTHIA8_lhapdfdummy_LIBRARY)

mark_as_advanced(PYTHIA8_FOUND PYTHIA8_INCLUDE_DIR PYTHIA8_LIBRARY PYTHIA8_hepmcinterface_LIBRARY PYTHIA8_lhapdfdummy_LIBRARY PYTHIA8_VERSION_CHECK)
