import zipfile
import os

def SetDirToBase():
    ## Get the filepath to the base repo folder and set it as the OS directory
    basefolder = os.path.dirname(os.path.dirname(__file__))
    os.chdir(basefolder)


def GetUserInputKMZFile():
    while True:
        infile = rf"{input('Please enter the path to your source KMZ file here: ')}"
        if os.path.exists(infile) and infile[-4:] == ".kmz":
            baseName = os.path.basename(infile)
            newPath = os.path.join("KMZ_Sourcefile", baseName)
            os.rename(infile, newPath)
            break
        else:
            print("Either the file you entered does not exist, or it's not a KMZ file. Please try again!")
    return baseName


def ExtractKMZToKML():
    SetDirToBase()
    ## Verify that the folder for source data exists
    if os.path.exists("KMZ_Sourcefile"):
        ## Pull existing files into a list
        existingFiles = os.listdir("KMZ_Sourcefile")
        ## Narrow down to kmzFiles
        kmzFiles = [f for f in existingFiles if ".kmz" in f]
        ## Get specified file, either the only one if there IS only one, or by user input
        if len(kmzFiles) > 1:
            ## Get the kmz file the user wants. Must ensure input is castable to int for indexing
            while True:
                fileIndex = rf"{input(f'Please enter the index of the KMZ you wish to unzip from the following list: {list(enumerate(kmzFiles))}  ')}"
                try:
                    fileIndex = int(fileIndex)
                    if fileIndex in range(len(kmzFiles)):
                        break
                    else:
                        print("Value entered fell outside the available indices. Please try again.")
                except:
                    print("Value entered could not be cast to Int! Please try again.")
            finalKMZ = kmzFiles[fileIndex]
        elif len(kmzFiles) == 1:
            finalKMZ = kmzFiles[0]
        ## If no KMZ files are found, go the user input route like if the folder doesn't exist (below)
        else:
            finalKMZ = GetUserInputKMZFile()
    ## If the KMZ_Sourcefile folder doesn't exist, create it and have the user 
    ## specify the source file to ccut/paste into this folder
    else:
        os.mkdir("KMZ_Sourcefile")
        finalKMZ = GetUserInputKMZFile()

    ## If a doc.kml file was previously extracted, delete it now (it's source KMZ will be untouched)
    if os.path.exists("KMZ_Sourcefile/doc.kml"):
        os.remove("KMZ_Sourcefile/doc.kml")

    ## Unzip KMZ file in the KMZ_Sourcefile folder to expose doc.kml
    with zipfile.ZipFile(os.path.join("KMZ_Sourcefile", finalKMZ),'r') as zip_ref:
        zip_ref.extractall("KMZ_Sourcefile")

    


def CompressKMLToKMZ(KMZName, KMLName="doc.kml"):
    """
    Keyword Args:
    - KMZName: Any string name to be applied to the KMZ file. The KML file within will retain its name
    - KMLName: The string name of the KML file to be written. By default, it will be named doc.kml
    """
    ## Create ZipFile object in with structure and add KMLName to the zip repository
    if not os.path.exists("_Output"):
        os.mkdir("_Output")
    if os.path.exists(rf"_Output\{KMZName}"):
        os.remove(rf"_Output\{KMZName}")
    with zipfile.ZipFile(rf"_Output\{KMZName}", 'w') as zip_ref:
        zip_ref.write(rf"KMZ_Sourcefile\{KMLName}")


if __name__ == "__main__":
    ExtractKMZToKML()