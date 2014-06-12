# - Locate yaml-cpp library
# Defines:
#
#  YAMLCPP_FOUND
#  YAMLCPP_INCLUDE_DIR
#  YAMLCPP_INCLUDE_DIRS (not cached)
#  YAMLCPP_LIBRARY
#  YAMLCPP_LIBRARIES (not cached)


find_path(YAMLCPP_INCLUDE_DIR yaml-cpp/yaml.h
          HINTS $ENV{YAMLCPP_ROOT_DIR}/include ${YAMLCPP_ROOT_DIR}/include)

find_library(YAMLCPP_LIBRARY NAMES yaml-cpp
             HINTS $ENV{YAMLCPP_ROOT_DIR}/lib ${YAMLCPP_ROOT_DIR}/lib)

set(YAMLCPP_INCLUDE_DIRS ${YAMLCPP_INCLUDE_DIR})
set(YAMLCPP_LIBRARIES ${YAMLCPP_LIBRARY})

# handle the QUIETLY and REQUIRED arguments and set YAMLCPP_FOUND to TRUE if
# all listed variables are TRUE

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(YAMLCPP DEFAULT_MSG YAMLCPP_LIBRARY YAMLCPP_INCLUDE_DIR)

mark_as_advanced(YAMLCPP_FOUND YAMLCPP_LIBRARY YAMLCPP_INCLUDE_DIR)