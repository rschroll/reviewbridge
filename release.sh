#!/bin/sh

mkdir -p release
sed -e 's/DEVEL = True/DEVEL = False/' \
    -e '/%INDEX_HTML%/ {
            r index.html
            d
        }' \
    -e '/%STYLE_CSS%/ {
            r style.css
            d
        }' reviewbridge.py > release/reviewbridge.py
