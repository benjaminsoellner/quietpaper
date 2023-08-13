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
    if [ ! -d ./venv3.9-quietpaper ]; then
        python3.9 -m venv venv3.9-quietpaper
        . venv3.9-quietpaper/bin/activate
        pip install --upgrade "pip==23.2.1"
        # I had problems installing Rust on Debian Stretch, so use an older version of 
        # cryptography that doesn't require it.
        CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install -r requirements.txt
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

    service quietpaper start

    popd >/dev/null 2>&1
)
