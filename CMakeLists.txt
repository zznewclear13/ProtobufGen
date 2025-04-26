cmake_minimum_required(VERSION 3.20.0 FATAL_ERROR)

set(PROTOBUF_GEN_NAME "ProtobufGen")
message("[${PROTOBUF_GEN_NAME}] CMake configuration begins...")

project(
    "Protobuf Gen"
    DESCRIPTION "A protobuf code generation project using CMake, Python and Jinja2."
    LANGUAGES CXX
)

if(NOT MSVC)
    message(FATAL_ERROR "This app currently only supports MSVC for building." )
endif()

find_package(Python REQUIRED)
if(NOT Python_FOUND)
    message(FATAL_ERROR "Python not found." )
endif()

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(CMAKE_CONFIGURATION_TYPES Debug Release)
set_property(DIRECTORY ${PROTOBUF_GEN_PROJECT_DIR} PROPERTY VS_STARTUP_PROJECT ${PROTOBUF_GEN_NAME})

set(PROTOBUF_GEN_PROJECT_DIR ${CMAKE_SOURCE_DIR})
set(PROTOBUF_GEN_SOURCE_DIR ${PROTOBUF_GEN_PROJECT_DIR}/source)
set(PROTOBUF_GEN_INCLUDE_DIR ${PROTOBUF_GEN_PROJECT_DIR}/include ${PROTOBUF_GEN_SOURCE_DIR})
set(PROTOBUF_GEN_LIBRARY_DIR ${PROTOBUF_GEN_PROJECT_DIR}/library)
set(PROTOBUF_GEN_BINARY_DIR ${PROTOBUF_GEN_PROJECT_DIR}/binary)
message("[${PROTOBUF_GEN_NAME}] PROJECT_DIR: ${PROTOBUF_GEN_PROJECT_DIR}")

foreach(config IN ITEMS ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER ${config} CONFIG)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${CONFIG} ${PROTOBUF_GEN_BINARY_DIR}/${config}/bin)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${CONFIG} ${PROTOBUF_GEN_BINARY_DIR}/${config}/dll)
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${CONFIG} ${PROTOBUF_GEN_BINARY_DIR}/${config}/lib)
endforeach()

add_subdirectory("library")
add_subdirectory("source")
