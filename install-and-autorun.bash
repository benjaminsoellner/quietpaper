#!/bin/bash
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    pushd $here >/dev/null 2>&1
    
    # create user and install dependencies
    if [[ ! $(id -u quietpaper) ]]; then
        sudo useradd quietpaper
        sudo adduser quietpaper spi
        sudo adduser quietpaper gpio
        sudo usermod -d /home/quietpaper quietpaper
        sudo mkdir -p /home/quietpaper
        sudo chown quietpaper:quietpaper /home/quietpaper
        sudo chown :quietpaper . -R
    fi

    # install venv
    if [[ ! -d ./venv3.9-quietpaper ]]; then
        python3.9 -m venv venv3.9-quietpaper
        . venv3.9-quietpaper/bin/activate
        pip install --upgrade "pip==23.2.1"
        pip install -r requirements.txt
        deactivate
    fi

    # configure tado
    ./configure_tado.bash

    # create log and output directories
    if [[ ! -d ./log ]]; then
        mkdir -p log
        mkdir -p output
        sudo chown -R :quietpaper log
        sudo chown -R :quietpaper output
        sudo chmod -R g+w log output 
    fi

    # install quietpaper daemon
    if [[ ! -f /etc/init.d/quietpaper ]]; then
        sudo cp ./quietpaperd /etc/init.d/quietpaper
        sudo sed -i -e "s%@APPDIR@%$here%g" /etc/init.d/quietpaper
        sudo sed -i -e "s%@APPBIN@%$here/quietpaper.bash%g" /etc/init.d/quietpaper
        sudo chmod +x /etc/init.d/quietpaper
        sudo update-rc.d quietpaper defaults
    fi

    sudo service quietpaper start

    popd >/dev/null 2>&1
)
