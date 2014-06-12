#  Try to find POWHEG-BOX
# Defines:
#
#  POWHEG-BOX_BINARY_PATH

find_path(POWHEG-BOX_BINARY_PATH NAMES ZZ Dijet
          HINTS ${powhegbox_home}/bin 
          PATH_SUFFIXES bin)

# handle the QUIETLY and REQUIRED arguments and set POWHEG-BOX_FOUND to TRUE if
# all listed variables are TRUE
include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(POWHEG-BOX DEFAULT_MSG POWHEG-BOX_BINARY_PATH)

mark_as_advanced(POWHEG-BOX_FOUND)
