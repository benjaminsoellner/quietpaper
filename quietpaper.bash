#!/bin/bash
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    source $here/venv-quietpaper/bin/activate
    PYTHONPATH=$here:$PYTHONPATH python3 quietpaper.py
)