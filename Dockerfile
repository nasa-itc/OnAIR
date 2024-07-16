FROM ubuntu:20.04

ARG USER_ID=1001
ARG GROUP_ID=1001

# Needed for a silent cmake install
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Add the host's user/group ID so that the host can easily access files created by the guest
# Checks if group_id already exists (thanks Romeo)
RUN if ! grep -q ${GROUP_ID} /etc/group ; then groupadd -g ${GROUP_ID} dev_user; fi
RUN useradd -l -u ${USER_ID} -g ${GROUP_ID} onair_dev
# Add a home directory for the user
RUN mkdir /home/onair_dev && \
    chown onair_dev /home/onair_dev

# TODO: add ssh with X forwarding

# Install
RUN \
  apt-get update && \
  apt-get -y upgrade

# Bare minimum to build/run cFS
RUN \
  apt-get install sudo && \
  apt-get install -y build-essential && \
  apt-get install -y gcc-multilib && \
  apt-get install -y git && \
  apt-get install -y cmake && \
  apt-get install -y xterm

# lcov: needed for cFS unit tests
# xxd: does hex dumps, just plain handy to have
RUN \
  apt-get install -y lcov && \
  apt-get install -y xxd

# OnAIR Dependencies
RUN \
  apt-get install -y python3.9 && \
  apt-get install -y python3.9-dev && \
  apt-get install -y python3-pip

# Add new packages to install here to prevent re-running previous instructions

RUN \
  pip3 install numpy

# Ensure that all packages are up to date after new packages have been added above
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y --fix-missing && \
  apt-get install -y wget && \
  rm -rf /var/lib/apt/lists/*

# Add user to sudoers so that they can up the mqueue depth
# RUN adduser onair_dev sudo
RUN sudo usermod -aG sudo onair_dev
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Make OnAir requirements file accessible by onair_dev user
COPY requirements_pip.txt /home/onair_dev/requirements_onair.txt
RUN chown onair_dev /home/onair_dev/requirements_onair.txt

USER onair_dev

# Python stuff is being installed for the local user
ENV PATH="${PATH}:/home/onair_dev/.local/bin"

# Install OnAIR deps
RUN python3.9 -m pip install --upgrade pip setuptools wheel
RUN python3.9 -m pip install --user -r /home/onair_dev/requirements_onair.txt

