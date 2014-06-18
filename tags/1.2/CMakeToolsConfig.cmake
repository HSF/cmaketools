# This is just a handy entry point to the CMakeTools modules.
# Usage:
#
# find_package(CMakeTools)
# UseCMakeTools()
#

if(NOT DEFINED CMakeTools_DIR)
  set(CMakeTools_DIR ${CMAKE_CURRENT_LIST_DIR}
      CACHE PATH "Location of the CMakeTools project.")
endif()

macro(UseCMakeTools)
  set(CMAKE_MODULE_PATH ${CMakeTools_DIR} ${GaudiProject_DIR}/modules ${CMAKE_MODULE_PATH})
endif()
