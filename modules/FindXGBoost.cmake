# - Locate XGBoost library
# Defines:
#
#  XGBoost_FOUND
#  XGBoost_INCLUDE_DIR
#  XGBoost_INCLUDE_DIRS (not cached)
#  XGBoost_LIBRARY
#  XGBoost_LIBRARIES (not cached)
#  XGBoost_LIBRARY_DIRS (not cached)


find_path(XGBoost_INCLUDE_DIR xgboost/c_api.h 
          HINTS $ENV{XGBoost_ROOT_DIR}/include ${XGBoost_ROOT_DIR}/include)

find_library(XGBoost_LIBRARY NAMES xgboost
             HINTS $ENV{XGBoost_ROOT_DIR}/lib ${XGBoost_ROOT_DIR}/lib)

# handle the QUIETLY and REQUIRED arguments and set XGBoost_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(XGBoost DEFAULT_MSG XGBoost_INCLUDE_DIR XGBoost_LIBRARY)

mark_as_advanced(XGBoost_FOUND XGBoost_INCLUDE_DIR XGBoost_LIBRARY )

set(XGBoost_INCLUDE_DIRS ${XGBoost_INCLUDE_DIR})
set(XGBoost_LIBRARIES ${XGBoost_LIBRARY})
get_filename_component(XGBoost_LIBRARY_DIRS ${XGBoost_LIBRARY} PATH)
