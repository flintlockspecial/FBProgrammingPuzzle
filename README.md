# FBProgrammingPuzzle
 Repo for GIS Analyst Programming Puzzle

## Scripts:
### 1) ExtractAndZipKMZFiles.py
This module contains functions for extracting and zipping KMZ files to KML and vice versa.
- #### GetUserInputKMZFile: 
    This function is used twice within ExtractKMZToKML. It uses basic text input and a while loop to validate the input, copying the user-input file from wherever it resides into the KMZ_Sourcefile folder of the repo structure.
- #### ExtractKMZToKML: 
    This function assumes the repo folder structure is in use. It sets the OS directory 2 levels up from itself and proceeds to identify the KMZ file to be extracted. If one or more is found in the KMZ_Sourcefile folder, it is assumed the user intends to use one of them since the repo clone has already been set up on their machine. If the KMZ_Sourcefile folder does not exist or is empty, the script will request that the user provides the path to the KMZ file they would like copied in and extracted via simple text input. If more than one KMZ file is present in the KMZ_Sourcefile folder, the script will ask the user to specify which one to use by inputting an index to match the enumerated list. 
- #### CompressKMLFileToKMZ:
    This function takes in the desired KMZ file name (i.e. Output.kmz) and, optionally, a specified KML file name (i.e. output.kml) and writes the KML file to the _Output subfolder of the repo folder structure, creating the subfolder if necessary. If no KML file is specified, it assumes the user intends to pack up doc.kml. The KML file **must** be in the KML_Sourcefile folder.

### 2) ParseAndModifyKML.py
The code is explained in depth in the comments. Basically it filters out, offsets, and creates a copy of the SPLICE Handhole point features, then iterates through all the line vertices and uses distance calculations to determine how to segment the line. Current errors include the following:\
    - [x] Offset should be 10 meters, but is closer to 40.\
    - [x] At 3 of the 4 right angles along the line, the calculations return a switchback rather than following the course of the line. I will need to determine if this is a problem with the line vertices themselves or with my calculation logic. Other than those two small errors, the outputs look great!\
    - [x] NEW PROBLEM: Switchbacks are fixed, but not the segments overshoot the point features after right angles by 1 vertex.\
        - Fixed by adding an additional condition checking for a measured distance to next vertex of 0. Vertices had been getting skipped before that by accident.\
    - [x] NEW PROBLEM: Got distance measruements added to segments, but they seem to be about 20 meters short of the real measurement. Will need to diagnose the DistBetweenCoords function as well.\
    - Turns out both the offset and distance measurement errors were because the coordinates are stored in KML as X,Y,Z rather than Lat(Y),Lon(X),Z. All I had to do was switch the referencing indices around when pulling the coordinates out and when rebuilding the coordinate strings, and it worked within the acceptable margin of error when considering projection onto a spherical Earth.

Runtime on the sample file was 0.13 seconds. I do not anticipate that changing when errors are corrected.

### 3) RunProgrammingPuzzle.bat
Simply a batch file to run the python scripts. Assumes the user has Python 3 on the PATH variable with pykml installed