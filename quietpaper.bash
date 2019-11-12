#!/bin/bash -l
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
positional=()
log="log"
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -l|--log)
    log="$2"
    shift 
    shift 
    positional+=("-l") 
    positional+=($log) 
    ;;
    *)
    positional+=("$1") 
    shift 
    ;;
esac
done
set -- "${positional[@]}"

(
    pushd $here >/dev/null 2>&1
    source venv-quietpaper/bin/activate
    while true ; do
        PYTHONPATH=$here:$PYTHONPATH stdbuf -oL python3 quietpaper.py $@
    done
    exit $?
    popd >/dev/null 2>&1
)
