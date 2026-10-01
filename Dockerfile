FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    gdb \
    clang \
    clangd \
    clang-format \
    clang-tidy \
    curl \
    lsb-release \
    software-properties-common \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# ROS 2 repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    > /etc/apt/sources.list.d/ros2.list

# ROS 2 Jazzy
RUN apt-get update && apt-get install -y \
    ros-jazzy-desktop \
    && rm -rf /var/lib/apt/lists/*

# Gazebo Harmonic repository
RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
    -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/gazebo-stable.list

# Gazebo Harmonic
RUN apt-get update && apt-get install -y \
    gz-harmonic \
    && rm -rf /var/lib/apt/lists/*

# Python3 dedicated virtual environment for build dependencies
RUN python3 -m venv /opt/colcon-venv

RUN /opt/colcon-venv/bin/pip install \
    colcon-common-extensions

ENV PATH="/opt/colcon-venv/bin:$PATH"

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

WORKDIR /workspace