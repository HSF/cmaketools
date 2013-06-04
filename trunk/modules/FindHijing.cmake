# - Locate photos library
# Defines:
#
#  HIJING_FOUND
#  HIJING_INCLUDE_DIR
#  HIJING_INCLUDE_DIRS (not cached)
#  HIJING_LIBRARY
#  HIJING_LIBRARIES (not cached)


find_library(HIJING_LIBRARY NAMES hijing
             HINTS $ENV{HIJING_ROOT_DIR}/lib ${HIJING_ROOT_DIR}/lib)

find_library(HIJING_dummy_LIBRARY NAMES hijing_dummy
             HINTS $ENV{HIJING_ROOT_DIR}/lib ${HIJING_ROOT_DIR}/lib)


set(HIJING_LIBRARIES ${HIJING_LIBRARY} ${HIJING_dummy_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set PHOTOS_FOUND to TRUE if
# all listed variables are TRUE

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(HIJING DEFAULT_MSG HIJING_LIBRARY HIJING_dummy_LIBRARY)

mark_as_advanced(HIJING_FOUND HIJING_LIBRARY HIJING_dummy_LIBRARY)
