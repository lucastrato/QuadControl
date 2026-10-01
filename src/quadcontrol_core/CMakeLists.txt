cmake_minimum_required(VERSION 3.8)
project(quadcontrol_core)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(CMAKE_BUILD_TYPE STREQUAL "StaticAnalysis")
    set(CMAKE_CXX_CLANG_TIDY clang-tidy)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

option(QUADCONTROL_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
option(QUADCONTROL_ENABLE_COVERAGE "Enable GCC coverage instrumentation" OFF)

if(QUADCONTROL_ENABLE_SANITIZERS AND QUADCONTROL_ENABLE_COVERAGE)
  message(FATAL_ERROR "Sanitizers and coverage instrumentation must use separate builds")
elseif(QUADCONTROL_ENABLE_SANITIZERS)
  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    message(FATAL_ERROR "Sanitizers require GCC or Clang")
  endif()
  add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
  set(CMAKE_EXE_LINKER_FLAGS
      "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address,undefined")
elseif(QUADCONTROL_ENABLE_COVERAGE)
  if(NOT CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(FATAL_ERROR "Coverage instrumentation currently requires GCC")
  endif()
  add_compile_options(--coverage -O0 -g)
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --coverage")
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

add_executable(controller src/controller.cpp)
target_include_directories(controller PRIVATE include)
add_executable(monitor src/monitor.cpp)

ament_target_dependencies(
  controller
  rclcpp
  std_msgs
  std_srvs
)

ament_target_dependencies(
  monitor
  rclcpp
  std_msgs
)

install(TARGETS
  controller
  monitor
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_counter test/test_counter.cpp)
  target_include_directories(test_counter PRIVATE include)

  find_package(launch_testing_ament_cmake REQUIRED)
  add_launch_test(
    test/test_nodes_launch.py
    TIMEOUT 60
    ARGS
    "controller_executable:=$<TARGET_FILE:controller>"
    "monitor_executable:=$<TARGET_FILE:monitor>"
  )

  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
