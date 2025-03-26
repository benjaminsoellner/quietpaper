#!/bin/bash
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    pushd $here >/dev/null 2>&1
    source venv3.9-quietpaper/bin/activate
    PYTHONPATH=$here:$PYTHONPATH stdbuf -oL python3.9 configure_tado.py $@
    exit $?
    popd >/dev/null 2>&1
)
