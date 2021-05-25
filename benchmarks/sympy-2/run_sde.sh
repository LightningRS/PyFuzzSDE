#!/bin/bash
export PYTHONPATH=$(pwd)/sympy:$(dirname $(dirname $(pwd)))
python run_sde.py
exit 0
