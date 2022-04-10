#!/bin/bash
pipenv install --deploy --ignore-pipfile

pipenv run migrate

pipenv run python3 main.py
