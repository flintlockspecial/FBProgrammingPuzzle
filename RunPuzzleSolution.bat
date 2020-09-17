@echo off
cd /D "%~dp0"

echo Running script to unpack KMZ file
python src/ExtractAndZipKMZFiles.py

echo Running puzzle solution via script src/ParseAndModifyKML.py
python src/ParseAndModifyKML.py

PAUSE