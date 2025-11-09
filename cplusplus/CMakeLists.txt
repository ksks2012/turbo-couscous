cmake_minimum_required(VERSION 3.16)
project(CircularChromosomeCompression 
    VERSION 1.0.0 
    DESCRIPTION "Bio-inspired compression algorithm based on dinoflagellate circular chromosomes"
    LANGUAGES CXX
)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic")
    set(CMAKE_CXX_FLAGS_DEBUG "-g3 -O0 -DDEBUG")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
endif()

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Library source files
set(CCC_SOURCES
    circular_chromosome_compression.cpp
)

set(CCC_HEADERS
    circular_chromosome_compression.h
)

# Create static library
add_library(ccc_static STATIC ${CCC_SOURCES})
target_include_directories(ccc_static PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
set_target_properties(ccc_static PROPERTIES
    OUTPUT_NAME ccc
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
)

# Create shared library (optional)
option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
if(BUILD_SHARED_LIBS)
    add_library(ccc_shared SHARED ${CCC_SOURCES})
    target_include_directories(ccc_shared PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
    set_target_properties(ccc_shared PROPERTIES
        OUTPUT_NAME ccc
        VERSION ${PROJECT_VERSION}
        SOVERSION 1
    )
endif()

# Test executable
option(BUILD_TESTS "Build test programs" ON)
if(BUILD_TESTS)
    add_executable(test_ccc ./tests/test_ccc_cpp.cpp)
    target_link_libraries(test_ccc ccc_static)
    set_target_properties(test_ccc PROPERTIES
        OUTPUT_NAME test_ccc
    )
    
    # Enable testing
    enable_testing()
    add_test(NAME ccc_unit_tests COMMAND test_ccc)
endif()

# Example executable
option(BUILD_EXAMPLES "Build example programs" ON)
if(BUILD_EXAMPLES)
    add_executable(ccc_example example_usage.cpp)
    target_link_libraries(ccc_example ccc_static)
    set_target_properties(ccc_example PROPERTIES
        OUTPUT_NAME ccc_example
    )
endif()

# Benchmark executables
option(BUILD_BENCHMARKS "Build benchmark programs" ON)
if(BUILD_BENCHMARKS)
    add_executable(large_file_benchmark large_file_benchmark.cpp)
    target_link_libraries(large_file_benchmark ccc_static)
    set_target_properties(large_file_benchmark PROPERTIES
        OUTPUT_NAME large_file_benchmark
    )
endif()

# Installation
option(INSTALL_CCC "Install CCC library and headers" ON)
if(INSTALL_CCC)
    include(GNUInstallDirs)
    
    # Install library
    install(TARGETS ccc_static
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    )
    
    if(BUILD_SHARED_LIBS)
        install(TARGETS ccc_shared
            ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
            LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
    
    # Install headers
    install(FILES ${CCC_HEADERS}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
    
    # Install executables
    if(BUILD_TESTS)
        install(TARGETS test_ccc
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
    
    if(BUILD_EXAMPLES)
        install(TARGETS ccc_example
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
    
    if(BUILD_BENCHMARKS)
        install(TARGETS large_file_benchmark
            RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
    endif()
    
    # Create pkg-config file
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/ccc.pc.in"
        "${CMAKE_CURRENT_BINARY_DIR}/ccc.pc"
        @ONLY
    )
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/ccc.pc"
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig
    )
endif()

# Documentation
option(BUILD_DOCS "Build documentation" OFF)
if(BUILD_DOCS)
    find_package(Doxygen)
    if(DOXYGEN_FOUND)
        configure_file(
            "${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in"
            "${CMAKE_CURRENT_BINARY_DIR}/Doxyfile"
            @ONLY
        )
        add_custom_target(docs
            ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Generating API documentation with Doxygen"
            VERBATIM
        )
    endif()
endif()

# Packaging (optional)
option(ENABLE_CPACK "Enable CPack packaging" OFF)
if(ENABLE_CPACK)
    set(CPACK_PACKAGE_NAME "circular-chromosome-compression")
    set(CPACK_PACKAGE_VENDOR "CCC Project")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Bio-inspired compression algorithm")
    set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
    
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
        set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
    endif()
    
    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
        set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")
    endif()
    
    include(CPack)
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "Configuration Summary:")
message(STATUS "  Project Name:    ${PROJECT_NAME}")
message(STATUS "  Version:         ${PROJECT_VERSION}")
message(STATUS "  Build Type:      ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ Standard:    ${CMAKE_CXX_STANDARD}")
message(STATUS "  Install Prefix:  ${CMAKE_INSTALL_PREFIX}")
message(STATUS "")
message(STATUS "Build Options:")
message(STATUS "  Build Tests:     ${BUILD_TESTS}")
message(STATUS "  Build Examples:  ${BUILD_EXAMPLES}")
message(STATUS "  Build Shared:    ${BUILD_SHARED_LIBS}")
message(STATUS "  Install CCC:     ${INSTALL_CCC}")
message(STATUS "  Build Docs:      ${BUILD_DOCS}")
message(STATUS "")
