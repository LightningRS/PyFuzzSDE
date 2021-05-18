#!/bin/bash
export PYTHONPATH=$(pwd):$(dirname $(dirname $(pwd)))
python run_sde.py
exit 0
