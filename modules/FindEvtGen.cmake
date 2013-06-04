# - Locate EvtGen library
# Defines:
#
#  EVTGEN_FOUND
#  EVTGEN_INCLUDE_DIR
#  EVTGEN_LIBRARY
#  EVTGEN_INCLUDE_DIRS (not cached)
#  EVTGEN_LIBRARIES (not cached)

find_path(EVTGEN_INCLUDE_DIR EvtGen/EvtGen.hh
          HINTS $ENV{EVTGEN_ROOT_DIR}/include/ ${EVTGEN_ROOT_DIR}/include/)

find_library(EVTGEN_LIBRARY NAMES EvtGen
             HINTS $ENV{EVTGEN_ROOT_DIR}/lib ${EVTGEN_ROOT_DIR}/lib)

set(EVTGEN_INCLUDE_DIRS ${EVTGEN_INCLUDE_DIR})
set(EVTGEN_LIBRARIES ${EVTGEN_LIBRARY})

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Evtgen DEFAULT_MSG EVTGEN_INCLUDE_DIR EVTGEN_LIBRARY)

mark_as_advanced(EVTGEN_FOUND EVTGEN_INCLUDE_DIR EVTGEN_LIBRARY)