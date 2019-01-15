###############################################################################
# (c) Copyright 2000-2018 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
# - Locate XGBoost library
# Defines:
#
#  XGBoost_FOUND
#  XGBoost_INCLUDE_DIR
#  XGBoost_INCLUDE_DIRS (not cached)
#  XGBoost_LIBRARY
#  XGBoost_LIBRARIES (not cached)
#  XGBoost_LIBRARY_DIRS (not cached)
#  XGBoost_EXTRA_INCLUDE_DIR


find_path(XGBoost_INCLUDE_DIR xgboost/c_api.h 
          HINTS $ENV{XGBoost_ROOT_DIR}/include ${XGBoost_ROOT_DIR}/include)

find_path(XGBoost_EXTRA_INCLUDE_DIR rabit/c_api.h
          HINTS ${XGBoost_INCLUDE_DIR}/../rabit/include 
	  $ENV{XGBoost_ROOT_DIR}/rabit/include ${XGBoost_ROOT_DIR}/rabit/include)

find_library(XGBoost_LIBRARY NAMES xgboost
             HINTS $ENV{XGBoost_ROOT_DIR}/lib ${XGBoost_ROOT_DIR}/lib)

# handle the QUIETLY and REQUIRED arguments and set XGBoost_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(XGBoost DEFAULT_MSG XGBoost_INCLUDE_DIR XGBoost_LIBRARY  XGBoost_EXTRA_INCLUDE_DIR)

mark_as_advanced(XGBoost_FOUND XGBoost_INCLUDE_DIR XGBoost_LIBRARY XGBoost_EXTRA_INCLUDE_DIR)

set(XGBoost_INCLUDE_DIRS ${XGBoost_INCLUDE_DIR} ${XGBoost_EXTRA_INCLUDE_DIR})
set(XGBoost_LIBRARIES ${XGBoost_LIBRARY})
get_filename_component(XGBoost_LIBRARY_DIRS ${XGBoost_LIBRARY} PATH)
