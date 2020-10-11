#!/bin/bash

cd data
kaggle competitions download -c test-recsys
unzip -q t\*zip -d .
rm -f *.zip
