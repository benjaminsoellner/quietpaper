#!/bin/bash -l
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    pushd $here >/dev/null 2>&1
    source venv-quietpaper/bin/activate
    while true ; do
        PYTHONPATH=$here:$PYTHONPATH stdbuf -oL python3 quietpaper.py $@
    done
    exit $?
    popd >/dev/null 2>&1
)
