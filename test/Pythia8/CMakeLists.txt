cmake_minimum_required(VERSION 3.3)

project(Pythia8CMakeTest)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/../../ ${CMAKE_CURRENT_LIST_DIR}/../../modules  ${CMAKE_MODULE_PATH})

find_package(Pythia8)


add_executable(Pythia8CMakeTestExe test.cc)
target_include_directories(Pythia8CMakeTestExe PRIVATE ${PYTHIA8_INCLUDE_DIRS})
target_link_libraries(Pythia8CMakeTestExe ${PYTHIA8_LIBRARIES})

