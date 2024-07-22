cmake_minimum_required(VERSION 3.26)
project(
    rtcamp10_samples
    VERSION 1.0
    DESCRIPTION "Sample code for RTCamp10"
    LANGUAGES C CXX)

set_property(GLOBAL PROPERTY USE_FOLDERS ON)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_RUNTIME_LIBRARY_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

add_subdirectory(samples/cpu_renderer)
