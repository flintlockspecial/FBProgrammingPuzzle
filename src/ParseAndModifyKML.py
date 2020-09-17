import copy
import os
import time
from ExtractAndZipKMZFiles import SetDirToBase, ExtractKMZToKML, CompressKMLToKMZ
from lxml import etree
from math import sin, cos, sqrt, atan2, radians, pi
from pykml import parser

t0 = time.time()

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


## TODO : Figure out and fix the Offset funciton - why is 10 meters turning into 40?

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

    ## Parse the KML file and get to the root
    kml_file = r"KMZ_Sourcefile\doc.kml"
    tree = parser.parse(kml_file)
    doc = tree.getroot()

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

    ## Get sequential order of point Placemarks
    pointPlacemarksSorted = sorted(
        pointPlacemarks, 
        key=lambda pm: int(
            str(pm.ExtendedData.SchemaData.SimpleData).split(" ")[-1].lstrip("D")
        )
    )

    ## Get all point coordinates for use segmenting line
    allPointCoords = list(reversed([
        (
            float(str(pm.Point.coordinates).split(",")[0]),
            float(str(pm.Point.coordinates).split(",")[1]) 
        ) for pm in pointPlacemarksSorted
    ]))
    
    ## Remove all placemarks from pointCopy that aren't SPLICE HH
    for placemark in pointPlacemarks:
        delInd = False
        for attr in placemark.ExtendedData.SchemaData.iterchildren():
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
        newCoordsString = f"{coordsO[0]},{coordsO[1]},0"
        placemark.Point.coordinates = newCoordsString
    
    ## Append the offset and reduced copy of the points layer to the SS_SpanD_HH.kml document
    pointDocument.append(pointCopy)
    
    ## Segment the line feature
    lineCopy = copy.deepcopy(linesDocument.Folder)
    lineCopy.name = "SS_SpanD_RL_Segmented"

    ## Pull floats of all the line coordinates
    allLineCoords = [
        (
            float(str(coordTriplet).split(",")[0]),
            float(str(coordTriplet).split(",")[1]) 
        ) for coordTriplet in str(lineCopy.Placemark.LineString.coordinates).strip('[r"\t", r"\n"]').split(" ")
    ]

    ## Make a template copy of the Line Placemark, emptying the coordinate string
    templateLinePlacemark = copy.deepcopy(lineCopy.Placemark)
    lineCopy.remove(lineCopy.Placemark)
    templateLinePlacemark.LineString.coordinates = ""

    ## TODO: Why are switchbacks being drawn near right angles? Fix that!

    vertCount = 0
    pointCount = 1
    count = 1
    dist = None
    currentSegmentCoords = [allLineCoords.pop(0)]
    for thisVertex in allLineCoords:
        vertCount += 1
        ## Compare the current vertex to the next point along the line
        thisPoint = allPointCoords[-1] if len(allPointCoords) > 0 else allLineCoords[-1]
        thisDist = DistBetweenCoords(
            thisVertex[0], thisVertex[1], 
            thisPoint[0], thisPoint[1]
        )

        ## Get the previous line vertex for failsafe check
        prevVertex = currentSegmentCoords[-1]
        prevVertDist = DistBetweenCoords(
            thisVertex[0], thisVertex[1], 
            prevVertex[0], prevVertex[1]
        )

        print(f"This vertex: {vertCount}")
        print(f"Previous Distance: {dist}")
        print(f"This Distance: {thisDist}")
        print(f"Distance to previous vertex: {prevVertDist}")

        ## If the previous distance is nulled overwrite and continue
        if not dist:
            print(f"Appending this vertex to coord list for segment {count}, Line Vertex: {vertCount}, Point Number: {pointCount}")
            currentSegmentCoords.append(thisVertex)
            dist = thisDist
        ## If the current distance to the next point is shorter than the previous,
        ## and if the distance to the previous vertex is shorter than the distance
        ## from that vertex to the current point, set distance to the current check
        ## and proceed to the next coordinate pair
        elif dist and (thisDist < dist and dist > prevVertDist):
            print(f"Appending this vertex to coord list for segment {count}, Line Vertex: {vertCount}, Point Number: {pointCount}")
            currentSegmentCoords.append(thisVertex)
            dist = thisDist
        ## If the current distance to the next point is longer than the previous,
        ## or if the distance to the previous vertex is longer than the distance
        ## from that vertex to the current point, the point has been overshot.
        ## Load a new Placemark section in lineCopy and reset the variables to
        ## continue this iteration
        elif (dist and (thisDist > dist or dist < prevVertDist)) or (len(allPointCoords) == 0 and thisDist < 1):
            print(f"Drawing segment {count}, Line Vertex: {vertCount}, Point Number: {pointCount}")
            if dist > 1:
                currentSegmentCoords.append(thisPoint)
            ## Create new deepcopy of the template line Placemark
            ## and set the name based on the current segment count
            newSegment = copy.deepcopy(templateLinePlacemark)
            newSegment.name = f"Southstar_Seg{count}"
            ## Create the new coordinate string
            firstPair = currentSegmentCoords.pop(0)
            coordstring = f"{firstPair[0]},{firstPair[1]},0"
            for coordPair in currentSegmentCoords:
                coordstring += f" {coordPair[0]},{coordPair[1]},0"
            ## Set coordinates in new Placemark
            newSegment.LineString.coordinates = coordstring
            ## Set length value
            length = 0
            for i, thisCoord in enumerate(currentSegmentCoords):
                try: 
                    nextCoord = currentSegmentCoords[i+1]
                except: 
                    break
                length += DistBetweenCoords(
                    thisCoord[0], thisCoord[1], 
                    nextCoord[0], nextCoord[1]
                )
            for attr in newSegment.ExtendedData.SchemaData.getchildren():
                if attr.values()[0] == "length":
                    attr._setText(f'{length * .00062137119224}')
            lineCopy.append(newSegment)

            ## Reset vertices if there are any more points to compare to
            if len(allPointCoords) > 0:
                count += 1
                currentSegmentCoords = [allPointCoords.pop(), thisVertex]
                pointCount += 1
                if len(allPointCoords) > 0:
                    nextPoint = allPointCoords[-1]
                    dist = DistBetweenCoords(
                        thisVertex[0], thisVertex[1], 
                        nextPoint[0], nextPoint[1]
                    )

    ## Append the copy of linesDocument to the root
    linesDocument.append(lineCopy)

    if os.path.exists("KMZ_Sourcefile/output.kml"):
        os.remove("KMZ_Sourcefile/output.kml")
    tree.write("KMZ_Sourcefile/output.kml")
    CompressKMLToKMZ("FBProgrammingPuzzleOutput.kmz", "output.kml")

if __name__ == '__main__':
    Main()

t1 = time.time()

print(f"Elapsed time = {t1 - t0}")
