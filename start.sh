#!/bin/bash
python3 -m pipenv install --deploy --ignore-pipfile

python3 -m pipenv run migrate

python3 -m pipenv run python3 main.py
