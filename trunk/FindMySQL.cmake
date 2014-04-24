# - Locate MySQL library
# Defines:
#
#  MYSQL_FOUND
#  MYSQL_INCLUDE_DIR
#  MYSQL_INCLUDE_DIRS (not cached)
#  MYSQL_LIBRARIES
#  MYSQL_LIBRARY_DIRS (not cached)

find_path(MYSQL_INCLUDE_DIR mysql.h)
find_library(MYSQL_LIBRARIES NAMES mysqlclient_r libmysql.lib)

set(MYSQL_INCLUDE_DIRS ${MYSQL_INCLUDE_DIR} ${MYSQL_INCLUDE_DIR}/mysql)
get_filename_component(MYSQL_LIBRARY_DIRS ${MYSQL_LIBRARIES} PATH)

# handle the QUIETLY and REQUIRED arguments and set MYSQL_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(MySQL DEFAULT_MSG MYSQL_INCLUDE_DIR MYSQL_LIBRARIES)

mark_as_advanced(MYSQL_FOUND MYSQL_INCLUDE_DIR MYSQL_LIBRARIES)
