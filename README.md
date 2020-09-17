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

### [TODO] ParseAndModifyKML.py

### [TODO] RunProgrammingPuzzle.bat