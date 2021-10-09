#!/bin/bash

set -e
set -x

get_deps () {
    sudo apt install -y emacs git docker ansible aptitude \
	 python3-venv software-properties-common \
	 python3.10-venv python3.10
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.8

    # populate public and private key manually.
    mkdir ~/.ssh
    touch ~/.ssh/id_rsa
    touch ~/.ssh/id_rsa.pub
    chmod 700 ~/.ssh
    chmod 644 ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa.pub
}

get_cnet () {
    git clone https://github.com/containernet/containernet.git
    cd containernet/ansible
    sudo ansible-playbook -i "localhost," -c local install.yml
    cd ..
    sudo make develop
}

make_venv () {
    DEV=~/dev
    mkdir -p $DEV/venv
    if [ ! -d $DEV/venv/containernet ]; then
	python3 -m venv $DEV/venv/containernet
    fi
    echo source $DEV/venv/containernet/bin/activate
}

$*

exit 0
