cmake_minimum_required(VERSION 3.20.0 FATAL_ERROR)


file(GLOB_RECURSE SOURCE_FILES *.cpp* *.h* *.hpp*)
list(FILTER SOURCE_FILES EXCLUDE REGEX ${PROTOBUF_GEN_SOURCE_DIR}/ProtoGen/*)

message("\n[${PROTOBUF_GEN_NAME}] Begin building Visual Studio filters: ")
foreach(SOURCE_FILE IN ITEMS ${SOURCE_FILES})
    get_filename_component(SOURCE_FILE_PATH "${SOURCE_FILE}" PATH)
    string(REPLACE "${CMAKE_CURRENT_SOURCE_DIR}" "" GROUP_PATH "${SOURCE_FILE_PATH}")
    string(REPLACE "/" "\\" GROUP_PATH "${GROUP_PATH}")
    message(${SOURCE_FILE})
    source_group("${GROUP_PATH}" FILES "${SOURCE_FILE}")
endforeach()
message("[${PROTOBUF_GEN_NAME}] End building Visual Studio filters.\n")

add_executable(${PROTOBUF_GEN_NAME} ${SOURCE_FILES})
target_include_directories(${PROTOBUF_GEN_NAME} PRIVATE ${PROTOBUF_GEN_INCLUDE_DIR})
target_link_directories(${PROTOBUF_GEN_NAME} PRIVATE ${PROTOBUF_GEN_LIBRARY_DIR})
set_target_properties(${PROTOBUF_GEN_NAME} PROPERTIES VS_DEBUGGER_COMMAND_ARGUMENTS "${PROTOBUF_GEN_PROJECT_DIR}/Resources")
#add_custom_command(
#    TARGET ${PROTOBUF_GEN_NAME} POST_BUILD
#    COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_RUNTIME_DLLS:${PROTOBUF_GEN_NAME}> $<TARGET_FILE_DIR:${PROTOBUF_GEN_NAME}>
#    COMMAND_EXPAND_LISTS
#)

foreach(config IN ITEMS ${CMAKE_CONFIGURATION_TYPES})
    add_custom_command(
        TARGET ${PROTOBUF_GEN_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove_directory ${PROTOBUF_GEN_BINARY_DIR}/${config}/bin/Resources
        COMMAND ${CMAKE_COMMAND} -E copy_directory
            ${PROTOBUF_GEN_PROJECT_DIR}/Resources
            ${PROTOBUF_GEN_BINARY_DIR}/${config}/bin/Resources
        COMMAND_EXPAND_LISTS
    )
endforeach()

add_subdirectory("ProtoGen")