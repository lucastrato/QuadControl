# QuadControl

QuadControl is a ROS 2 C++ project for developing and testing a simulated
quadrotor control system.

## Overview

The project is designed as a software-only robotics environment using:

- ROS 2 Jazzy
- C++17
- Docker
- Gazebo
- CMake
- GoogleTest
- ROS 2 launch testing
- clangd and clang-tidy
- AddressSanitizer and UndefinedBehaviorSanitizer
- Code coverage
- Doxygen

## Nodes

### Controller

The `controller` node implements the control-loop component.

It:

- publishes the `/control_counter` topic
- provides the `/reset_counter` service
- executes its control loop periodically

### Monitor

The `monitor` node subscribes to `/control_counter` and reports received
counter values.

## Testing

The project contains:

- C++ unit tests using GoogleTest
- ROS 2 integration tests using `launch_testing`
- static analysis using clang-tidy
- runtime checks using AddressSanitizer and UndefinedBehaviorSanitizer
- code coverage instrumentation

## Development

The project is developed inside a Docker-based development environment and
can be built using the ROS 2 `colcon` build system.

## Documentation

This documentation is generated automatically using Doxygen.