#!/bin/bash
yum clean all
yum -y remove PackageKit
curl -O https://bootstrap.pypa.io/get-pip.py
python2.7 get-pip.py
yum clean all
yum -y install python27-pip.noarch
yum -y install python27-numpy.x86_64
yum -y install python27-scipy.x86_64 
pip  install py4j
pip  install boto
yum -y instal  aws-cli

yum -y install git
git clone https://github.com/jameslyons/python_speech_features.git 
easy_install-2.7 /python_speech_features/
easy_install /python_speech_features/
