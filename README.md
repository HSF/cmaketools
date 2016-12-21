This is a small package containing some commonly used CMake "find" modules.

To use them, you need to have the top directory in the CMAKE_PREFIX_PATH, then
you can enable the modules in your CMakeLists.txt with something like:

    find_package(CMakeTools)
    UseCMakeTools()
