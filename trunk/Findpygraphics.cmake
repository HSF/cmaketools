# - Simple module to add the pygraphics directory to the python path
#
# It also provides the functions gen_pyqt_resource and gen_pyqt_uic.
#
# The following variables are defined:
#
#   PYGRAPHICS_FOUND
#

set(PYGRAPHICS_FOUND 1)
set(PYGRAPHICS_PYTHON_PATH ${pygraphics_home}/lib/python${Python_config_version_twodigit}/site-packages
    CACHE PATH "Path to the pygraphics LCG package")

mark_as_advanced(PYGRAPHICS_FOUND PYGRAPHICS_PYTHON_PATH)

# Provides functions to compile .qrc and .ui files into Python modules.

find_package(PythonInterp QUIET REQUIRED)

find_program(pyrcc_cmd pyrcc4)
set(pyuic_cmd ${PYTHON_EXECUTABLE} -m PyQt4.uic.pyuic)

# gen_pyqt_resource(target output_dir inputs ...)
#
# Translate the .qrc files declared as inputs into Python modules in the specified
# output directory in the install prefix python directory.
# The target name is the target under which the generation should be grouped.
#
# Example:
#
#   gen_pyqt_resource(MyPackageResources MyPackage qt_resources/*.qrc)
#
# produces a target call MyPackageResources that creates the files *_rc.py in
# the directory python/MyPackage.
#
function(gen_pyqt_resource target outdir)
  if(ARGC LESS 3)
    message(FATAL_ERROR "gen_pyqt_resource requires at least 3 arguments.")
  endif()

  if(pyrcc_cmd)
    # prepare the directory needed to host the generated files
    file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/python/${outdir})

    # expand the wildcards for the input files
    file(GLOB inputs ${ARGN})
    set(outputs)

    # create one command and target for each file
    foreach(input ${inputs})
      get_filename_component(prefix ${input} NAME_WE)
      set(output ${CMAKE_BINARY_DIR}/python/${outdir}/${prefix}_rc.py)

      #message(STATUS "gen_pyqt_resouce ${target} ==> ${input} -> ${output}")
      set(cmd ${pyrcc_cmd} -o ${output} ${input})
      if(env_cmd)
        set(cmd ${env_cmd} --xml ${env_xml} ${cmd})
      endif()
      add_custom_command(OUTPUT ${output}
                         COMMAND ${cmd}
                         DEPENDS ${input})

      list(APPEND outputs ${output})
      #install(FILES ${output} DESTINATION ${outdir})
    endforeach()

    # Create the grouping target
    add_custom_target(${target} ALL DEPENDS ${outputs})

    # install the generated files
    install(FILES ${outputs} DESTINATION python/${outdir})
  else()
    message(FATAL_ERROR "The command pyrcc4 is not available.")
  endif()
endfunction()

# gen_pyqt_uic(target output_dir inputs ...)
#
# Translate the .ui files declared as inputs into Python modules in the specified
# output directory in the install prefix python directory.
# The target name is the target under which the generation should be grouped.
#
# Example:
#
#   gen_pyqt_uic(MyPackageUi MyPackage qt_resources/*.ui)
#
# produces a target call MyPackageUi that creates the files Ui_*.py in
# the directory python/MyPackage.
#
function(gen_pyqt_uic target outdir)
  if(ARGC LESS 3)
    message(FATAL_ERROR "gen_pyqt_uic requires at least 3 arguments.")
  endif()

  # prepare the directory needed to host the generated files
  file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/python/${outdir})

  # expand the wildcards for the input files
  file(GLOB inputs ${ARGN})
  set(outputs)

  # create one command and target for each file
  foreach(input ${inputs})
    get_filename_component(prefix ${input} NAME_WE)
    set(output ${CMAKE_BINARY_DIR}/python/${outdir}/Ui_${prefix}.py)

    #message(STATUS "gen_pyqt_uic ${target} ==> ${input} -> ${output}")
    set(cmd ${pyuic_cmd} -o ${output} ${input})
    if(env_cmd)
      set(cmd ${env_cmd} --xml ${env_xml} ${cmd})
    endif()
    add_custom_command(OUTPUT ${output}
                       COMMAND ${cmd}
                       DEPENDS ${input})

    list(APPEND outputs ${output})
    #install(FILES ${output} DESTINATION ${outdir})
  endforeach()

  # Create the grouping target
  add_custom_target(${target} ALL DEPENDS ${outputs})

  # install the generated files
  install(FILES ${outputs} DESTINATION python/${outdir})
endfunction()
