#!/bin/sh
# Build the single file executable for the platform this runs on.
# The recipe itself lives in SortMyShit.spec, so CI builds exactly the same thing.
pyinstaller SortMyShit.spec \
    --distpath=.packaged/dist \
    --workpath=.packaged/build \
    --clean \
    --noconfirm
