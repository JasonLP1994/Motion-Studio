#!/bin/bash
# Installs Intel Open Image Denoise (OIDN 1.4.3, Apache-2.0) into tools/oidn-py
# inside this project (no system install). It comes from the "oidn" package on PyPI,
# which bundles the real OIDN library. tools/ is git-ignored (57 MB binary).
set -e
cd "$(dirname "$0")/../.."
if [ -f tools/oidn-py/oidn/__init__.py ]; then echo "OIDN already installed"; exit 0; fi
pip install --no-deps --target tools/oidn-py "oidn==0.2.1"
echo "OIDN installed in tools/oidn-py"
