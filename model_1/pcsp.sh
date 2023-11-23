#!/bin/bash

# Needs to be ran on Linux OS with PAT Cli
# Do mv/cp files(*.pcsp) from ~/pcsp_files directory to directory with PAT cli
# Create new directory for validation file output
dest="pcsp_out/"
mkdir -p "$dest"

# After running verification store all output as txt file to pcsp_out
for file in *.pcsp; do
  mono PAT3.Console.exe -pcsp "$file" ${dest}"$(basename "$file" .pcsp).txt"
done

