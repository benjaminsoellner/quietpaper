#!/bin/bash
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    pushd $here >/dev/null 2>&1
    
    # create user
    if [ ! $(id -u quietpaper) ]; then
        useradd quietpaper
        adduser quietpaper spi
        adduser quietpaper gpio
        usermod -d /home/quietpaper quietpaper
        mkdir -p /home/quietpaper
        chown quietpaper:quietpaper /home/quietpaper
        chown :quietpaper . -R
    fi

    # install venv
    if [ ! -d ./venv-quietpaper ]; then
        python3 -m virtualenv venv-quietpaper
        . venv-quietpaper/bin/activate
        pip3 install -r requirements.txt
        deactivate
    fi

    # create log and output directories
    if [! -d ./log ]; then
        mkdir -p log
        mkdir -p output
        chown :quietpaper log
        chown :quietpaper output
        chmod g+w log output 
        chown g+w
    fi

    # install quietpaper daemon
    if [ ! -f /etc/init.d/quietpaper ]; then
        cp ./quietpaperd /etc/init.d/quietpaper
        sed -i -e "s%@APPDIR@%$here%g" /etc/init.d/quietpaper
        sed -i -e "s%@APPBIN@%$here/quietpaper.bash%g" /etc/init.d/quietpaper
        chmod +x /etc/init.d/quietpaper
        update-rc.d quietpaper defaults
    fi

    # install dependencies for hafasglue
    ( 
        pushd ./hafas-glue >/dev/null 2>&1
        npm install .
        popd >/dev/null 
    )
    
    # install hafasglue daemon
    if [ ! -f /etc/init.d/hafasglue ]; then
        cp ./hafasglued /etc/init.d/hafasglue
        sed -i -e "s%@APPDIR@%$here%g" /etc/init.d/hafasglue
        sed -i -e "s%@APPBIN@%$here/hafasglue.bash%g" /etc/init.d/hafasglue
        chmod +x /etc/init.d/hafasglue
        update-rc.d hafasglue defaults
    fi

    service hafasglue start
    service quietpaper start

    popd >/dev/null 2>&1
)
