#!/bin/bash

find ./ -name "*.pyc" | xargs rm -f
find ./ -name "*~" | xargs rm -f
find ./ -name "dropin.cache" | xargs rm -f
find ./ -name "_trial_temp" | xargs rm -rf
find ./ -name "*.log" | xargs rm -rf
find ./ -name "*.log.*" | xargs rm -rf
rm generated/*.py
