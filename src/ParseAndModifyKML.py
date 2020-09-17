import copy
import os
from ExtractAndZipKMZFiles import SetDirToBase, ExtractKMZToKML, CompressKMLToKMZ
from lxml import etree
from math import sin, cos, sqrt, atan2, radians, pi
from pykml import parser

def DistBetweenCoords(lat1, lon1, lat2, lon2):
    ## Approximate radius of earth in meters
    R = 6378137
    ## Convert lat/lon values to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    ## Get difference between lon and lat values
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    ## Perform trig to find the distance between the two points
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    ## Find distance in meters
    distance = R * c
    return distance


def OffsetCoordsByMeters(lat, lon, dn=10, de=10):
    ##Earth’s radius, sphere, meters
    R=6378137
    ##Coordinate offsets in radians
    dLat = dn/R
    dLon = de/(R*cos(pi*lat/180))
    ##OffsetPosition, decimal degrees
    latO = lat + dLat * 180/pi
    lonO = lon + dLon * 180/pi
    return [latO, lonO]


def Main():
    SetDirToBase()

    kml_file = r"KMZ_Sourcefile\doc.kml"
    doc = parser.parse(kml_file).getroot()
    ## Namespace tag will be necessary for any find operations
    ns = doc.tag.rstrip('kml')

    ## Get the two documents under the main folder (SS_SpanD_HH.kml and SS_SpanD_RL.kml)
    subDocuments = doc.Folder.findall(f"{ns}Document")

    pointDocIndex = 0
    linesDocIndex = 1

    ## Isolate the point and line documents by name
    pointDocument = subDocuments[pointDocIndex]
    linesDocument = subDocuments[linesDocIndex]

    ## Make a deepcopy of the point document and change the name
    pointCopy = copy.deepcopy(pointDocument.Folder)
    pointCopy.name = "SS_SpanD_HH_SpliceOffset"

    pointPlacemarks = pointCopy.findall(f"{ns}Placemark")

    ## Get all point coordinates for use segmenting line
    allPointCoords = [
        (
            float(str(pm.Point.coordinates).split(",")[0]),
            float(str(pm.Point.coordinates).split(",")[1]) 
        ) for pm in pointPlacemarks]
    
    ## Remove all placemarks from pointCopy that aren't SPLICE HH
    for placemark in pointPlacemarks:
        delInd = False
        for attr in pm.ExtendedData.SchemaData.iterchildren():
            if attr.values()[0] == 'HH_ID' and not "SPLICE" in str(attr):
                delInd = True
        if delInd:
            pointCopy.remove(placemark)
    
    if len(pointCopy.getchildren()) > 9:
        print("DEBUG: All the non_SPLICE points may not have been deleted!")

    ## Offset the coordinates of all SPLICE HH records
    for placemark in pointCopy.findall(f"{ns}Placemark"):
        coords = [ 
            float(str(placemark.Point.coordinates).split(",")[0]),
            float(str(placemark.Point.coordinates).split(",")[1])
        ]
        ## Offset the coordinates by the default of 10 meters
        coordsO = OffsetCoordsByMeters(coords[0], coords[1])
        newCoordsString = f"{coordso[0]},{coordsO[1]},0"
        placemark.Point.coordinates = newCoordsString
    
    ## Append the offset and reduced copy of the points layer to the SS_SpanD_HH.kml document
    pointDocument.append(pointCopy)
    
    ## TODO Code Logic
    ## To segment line:
    ##    Iterate through line vertices
    ##      1) Check distance to next point vertex
    ##      2) If distance less than previous, pop out into list for current segment
    ##      3) If distance greater, pause and create segment from all vertices in current segment list, 
    ##           final vertext being that of the point
    ##      4) Continue on, comparing to next point