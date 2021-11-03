FROM ubuntu:18.04
LABEL maintainer="vincnardelli@gmail.com"
# Upgrade installed packages
RUN apt-get update && apt-get upgrade -y && apt-get clean

# (...)

# Python package management and basic dependencies
RUN DEBIAN_FRONTEND="noninteractive" TZ="Europe" apt-get install -y curl python3.7 python3.7-dev python3.7-distutils build-essential locales git ghostscript python3-tk python3-opencv

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/'        /etc/locale.gen \
 && sed -i -e 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen

# Register the version in alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1

# Set python 3 as the default python
RUN update-alternatives --set python /usr/bin/python3.7

# Upgrade pip to latest version
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py

# Install packages
RUN pip install numpy matplotlib pandas beautifulsoup4 camelot-py[base] PyMuPDF scikit-learn adjustText