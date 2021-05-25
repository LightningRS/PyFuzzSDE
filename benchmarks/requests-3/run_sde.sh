#!/bin/bash
export PYTHONPATH=$(pwd)/requests:$(dirname $(dirname $(pwd)))
python run_sde.py
exit 0
