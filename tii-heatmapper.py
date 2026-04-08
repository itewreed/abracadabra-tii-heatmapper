import csv
import json
import argparse
import os

# ToDo
# DONE: Make an option, to disable drawing of secondary transmitters

parser = argparse.ArgumentParser(description='tii heatmap visualization')

parser.add_argument(
    "--csv",
    type=str,
    dest="csv",
    metavar="TII Measurements in CSV format",
    default="None",
    help="File with recordings of TII data and geolocation (Abracadabra TII records)",
)

parser.add_argument(
    "--tii",
    type=int,
    dest="tii",
    metavar="Select one tii for processing",
    default="0",
    help="Limit processing to one tii ID",
)

parser.add_argument(
    "--tiilist",
    dest="tiilist",
    action="store_true",
    default=False,
    help="List available tii IDs of the CSV dataset",
)

parser.add_argument(
    "--primary",
    dest="primary",
    action="store_true",
    default=False,
    help="List available tii IDs of the CSV dataset",
)
args = parser.parse_args()


if os.path.isfile(args.csv):
    with open(args.csv) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        sortedlist = sorted(reader, key=lambda row:(row['Main'],row['Sub']), reverse=False)
        if not args.tii == 0:
            tiiId = str(args.tii)
            jsonFile = args.csv.replace(".csv","_" + tiiId + ".json")
        else:
            jsonFile = args.csv.replace(".csv",".json")
else:
    print(args.csv + " Does not exist. Abort")
    exit(2)


data = {
    "type" : "FeatureCollection",
    "features" : [
         ]
    }
dataPoint = {
    "type" : "FeatureCollection",
    "features" : [
    ]
    }
dataRxPoint = {
    "type" : "FeatureCollection",
    "features" : [
    ]
    }
dataLine = {
    "type" : "FeatureCollection",
    "features" : [
    ]
    }
dataPoly = {
    "type" : "FeatureCollection",
    "features" : [
    ]
    }

tii = 0
tiicount = 0
tiiStats = {}
CreatePolygon = False

for tiis in sortedlist:
    # discard datasets with empty transmitter entries in csv file
    if tiis['Latitude (TX)'] != '' or tiis['Longitude (TX)'] != '':
        # on tii change in dataset, save previous tii and datapoints counted for it
        if int(tiis['Main']) * 100 + int(tiis['Sub']) != tii: 
            tiiStats[tii] = (tiicount)
            tiicount = 0
            tii = int(tiis['Main']) * 100 + int(tiis['Sub'])
        tiicount = tiicount + 1
# to get the last tii and datapoints count
tiiStats[tii] = (tiicount)
# remove first dataset, because it's 0 (tii = 0)
tiiStats.pop(0)

# process only one tii
if not args.tii == 0:
    print("Process only this tii an throw the rest away")
    if tiiStats[args.tii]:
        tiiStatsHelper = {args.tii : tiiStats[args.tii] }
        tiiStats = tiiStatsHelper
        print(tiiStatsHelper)
    else:
        print("Error, given tii not found in dataset. Abort!")
        exit(2)

# List available tii
if args.tiilist:
    print("Available tii and amount of datapoints per tii")
    for tii in tiiStats:
        print("tii:")
        print(tii)
        print("Datapoints:")
        print(tiiStats[tii])
    exit(0)

featuresArray = 0
for tii in tiiStats:
    CreatePointObj = True
    CreateLineObj = True
    CreatePolygonObj = True
    # reduce the points for drawing a polygon, for less jitter
    # drawing polygons is jittery anyway
    polyPoints = int((tiiStats[tii]) / 4)
    polyCounter = 0

    # create all the geo points
    for row in sortedlist:
        tii_row = (int(row['Main']) * 100 + int(row['Sub']))
        if (row['Latitude (TX)'] != '' or row['Longitude (TX)']) and (tii_row == tii):
            # Create the transmitter Point
            if CreatePointObj == True:
                dataPoint['features'].append(
                    {
                        "type" : "Feature",
                        "properties": {
                            row['Location']: str(tii)
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                float(row['Longitude (TX)']),
                                float(row['Latitude (TX)'])
                            ]
                        },
                    }
                )
                LonTx = float(row['Longitude (TX)'])
                LatTx = float(row['Latitude (TX)'])
                CreatePointObj = False
            
            # Define color palette for SNR values
            # Only color the primary received transmitter
            snrColor = "rgba(0, 0, 0, 0)"
            if float(row['Level [dB]']) >= 0.0:
                if float(row['SNR [dB]']) > 15.0:
                    # green
                    snrColor = "rgba(7, 219, 0, 1)"
                elif  (float(row['SNR [dB]'])) <= 15.0 and (float(row['SNR [dB]']) > 10.0):
                    # yellow
                    snrColor = "rgba(202, 220, 0, 1)"
                elif  (float(row['SNR [dB]'])) <= 10.0 and (float(row['SNR [dB]']) > 6.0):
                    # orange
                    snrColor = "rgba(215, 180, 0, 1)"
                else:
                    # red
                    snrColor = "rgba(219, 90, 0, 1)"
            else:
                # Color non primary reception in grey
                snrColor = "rgba(191, 191, 191, 1)"
            
            if args.primary:
                # Create Receiver point objects, only primary transmitter
                if float(row['Level [dB]']) >= 0.0:
                    dataRxPoint['features'].append(
                            {
                                "type" : "Feature",
                                "properties": {
                                    tii_row: tii_row,
                                    "marker-color" : snrColor,
                                    "marker-size" : "small"
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        float(row['Longitude (RX)']),
                                        float(row['Latitude (RX)'])
                                    ]
                                },
                            }
                        )
            else:
                # Create Receiver point objects
                dataRxPoint['features'].append(
                        {
                            "type" : "Feature",
                            "properties": {
                                tii_row: tii_row,
                                "marker-color" : snrColor,
                                "marker-size" : "small"
                            },
                            "geometry": {
                                "type": "Point",
                                "coordinates": [
                                    float(row['Longitude (RX)']),
                                    float(row['Latitude (RX)'])
                                ]
                            },
                        }
                    )
            
            ## Create Receiver line object
            #if CreateLineObj == True:
            #    dataLine['features'].append(
            #        {
            #            "type" : "Feature",
            #            "properties": {
            #                tii : row['Location']
            #            },
            #            "geometry": {
            #                "type": "LineString",
            #                "coordinates": [
            #                    [
            #                        float(row["Longitude (RX)"]),
            #                        float(row['Latitude (RX)'])
            #                    ]
            #                ]
            #            }
            #        }
            #    )
            #    CreateLineObj = False
            #else:
            #    # Fill object with coordinates
            #    dataLine['features'][featuresArray]['geometry']['coordinates'].append(
            #    [
            #        float(row['Longitude (RX)']),
            #        float(row['Latitude (RX)'])
            #    ]
            #)

            # Create Polygon object
            # Transmitter is starting point
            if CreatePolygonObj == True:
                dataPoly['features'].append(
                    {
                        "type" : "Feature",
                        "properties": {
                            tii : row['Location']
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        float(row['Longitude (TX)']),
                                        float(row['Latitude (TX)'])
                                    ],
                                    [
                                        float(row['Longitude (RX)']),
                                        float(row['Latitude (RX)'])
                                    ]
                                ]
                            ]
                        }
                    }
                )
                CreatePolygonObj = False
            else:
                # Fill polygon object with 3 + 2 coordinates
                if polyCounter == polyPoints:
                    polyCounter = 0
                    dataPoly['features'][featuresArray]['geometry']['coordinates'][0].append(
                        [
                            float(row['Longitude (RX)']),
                            float(row['Latitude (RX)'])
                        ]
                    )
            polyCounter = polyCounter + 1     

    # Finish Polygon object. Transmitter is endpoint
    dataPoly['features'][featuresArray]['geometry']['coordinates'][0].append(
        [
            LonTx,
            LatTx
        ]
    )
         
    featuresArray = featuresArray + 1

# Put all objects into one main object
data['features'].extend(dataPoint['features'])
data['features'].extend(dataRxPoint['features'])
#data['features'].extend(dataLine['features'])
data['features'].extend(dataPoly['features'])

# Save Geo json file
# If one tii is selected, tii id will be put into filename
with open(jsonFile, 'w') as file:
    json.dump(data, file, indent=4)