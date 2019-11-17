#!/bin/bash -l
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
(
    pushd $here >/dev/null 2>&1
    while true ; do
        node ./hafasglue/hafasglue.js
    done
    exit $?
    popd >/dev/null 2>&1
)
