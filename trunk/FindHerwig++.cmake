# - Try to find Herwig++
# Defines:
#
#  HERWIG++_FOUND
#  HERWIG++_EXECUTABLE
#  HERWIG++_BINARY_PATH (not cached)
#  HERWIG++_HOME (not cached)
#  HERWIG++_INCLUDE_DIR
#  HERWIG++_INCLUDE_DIRS (not cached)
#  HERWIG++_LIBRARY_DIR
#  HERWIG++_LIBRARY_DIRS (not cached)

find_program(HERWIG++_EXECUTABLE Herwig++
             HINTS ${HERWIG++_ROOT_DIR}/bin
                   $ENV{HERWIGPP_ROOT_DIR}/bin
                   ${HERWIGPP_ROOT_DIR}/bin)
if(HERWIG++_EXECUTABLE)
  get_filename_component(HERWIG++_BINARY_PATH ${HERWIG++_EXECUTABLE} PATH)
endif()

find_file(HERWIG++_INCLUDE_DIR Herwig++
          HINTS ${HERWIG++_ROOT_DIR}/include
                $ENV{HERWIGPP_ROOT_DIR}/include
                ${HERWIGPP_ROOT_DIR}/include
          PATH_SUFFIXES include)
set(HERWIG++_INCLUDE_DIRS ${HERWIG++_INCLUDE_DIR})
find_file(HERWIG++_LIBRARY_DIR Herwig++
          HINTS ${HERWIG++_ROOT_DIR}/lib
                $ENV{HERWIGPP_ROOT_DIR}/lib
                ${HERWIGPP_ROOT_DIR}/lib
          PATH_SUFFIXES lib)
set(HERWIG++_LIBRARY_DIRS ${HERWIG++_LIBRARY_DIR})
 
mark_as_advanced(HERWIG++_EXECUTABLE HERWIG++_INCLUDE_DIR HERWIG++_LIBRARY_DIR HERWIG++_EXECUTABLE)

# handle the QUIETLY and REQUIRED arguments and set HERWIG++_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Herwig++ DEFAULT_MSG HERWIG++_INCLUDE_DIR HERWIG++_LIBRARY_DIR)

mark_as_advanced(HERWIG++_FOUND)
