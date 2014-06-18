# - Locate Oracle library
# Defines:
#
#  ORACLE_FOUND
#  ORACLE_INCLUDE_DIR
#  ORACLE_INCLUDE_DIRS (not cached)
#  ORACLE_LIBRARY
#  ORACLE_LIBRARIES (not cached)
#  ORACLE_LIBRARY_DIRS (not cached)
#  SQLPLUS_EXECUTABLE

find_path(ORACLE_INCLUDE_DIR oci.h)
find_library(ORACLE_LIBRARY NAMES clntsh oci)
find_program(SQLPLUS_EXECUTABLE NAMES sqlplus
             HINTS ${ORACLE_INCLUDE_DIR}/../bin)

# handle the QUIETLY and REQUIRED arguments and set ORACLE_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Oracle DEFAULT_MSG ORACLE_INCLUDE_DIR ORACLE_LIBRARY)

mark_as_advanced(ORACLE_FOUND ORACLE_INCLUDE_DIR ORACLE_LIBRARY SQLPLUS_EXECUTABLE)

set(ORACLE_INCLUDE_DIRS ${ORACLE_INCLUDE_DIR})
get_filename_component(ORACLE_LIBRARY_DIRS ${ORACLE_LIBRARY} PATH)

set(ORACLE_LIBRARIES ${ORACLE_LIBRARY})

# Shall we handle these environment variables?
#set TNS_ADMIN $(oracle_home)/admin
#macro_append oracle_export_paths " $(TNS_ADMIN) " ATLAS ""
#
#set ORA_FPU_PRECISION  'EXTENDED'
#set NLS_LANG           'AMERICAN_AMERICA.WE8ISO8859P1'

