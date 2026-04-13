import csv
import json
import argparse
import os

def draw_point_transmitter(tx_name: str, tx_channel: str, tx_tii: int, tx_lon: float, tx_lat: float):
    tx_point = (
        {
            "type" : "Feature",
            "properties": {
                "Transmitter" : tx_name,
                "Channel"     : tx_channel,
                "Tii"         : tx_tii
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    tx_lon,
                    tx_lat
                ]
            },
        }
    )
                    
    return tx_point

def draw_point_receiver(tx_channel: str, tx_tii: int, rx_snr: float, snr_color: str, rx_lon: float, rx_lat: float):
    rx_point = (
        {
            "type" : "Feature",
            "properties": {
                "Channel" : tx_channel,
                "Tii": tx_tii,
                "Signalstrength": rx_snr,
                "markercolor" : snr_color,
                "markersize" : "small"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    rx_lon,
                    rx_lat
                ]
            },
        }
    )

    return rx_point

    
def snr_colorpalette(rx_snr: float, rx_level: float):
    if float(rx_level) >= 0.0:
        if float(rx_snr) > 15.0:
            # green
            snr_color = "rgba(7, 219, 0, 1)"
        elif  (float(rx_snr) <= 15.0 and (rx_snr) > 10.0):
            # yellow
            snr_color = "rgba(202, 220, 0, 1)"
        elif  (float(rx_snr)) <= 10.0 and (float(rx_snr) > 6.0):
            # orange
            snr_color = "rgba(215, 180, 0, 1)"
        else:
            # red
            snr_color = "rgba(219, 90, 0, 1)"
    else:
        # Color non primary reception in grey
        snr_color = "rgba(191, 191, 191, 1)"    

    return snr_color

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
        sortedListPoly = sorted(sortedlist, key=lambda row:(row['Main'],row['Sub'],row['Azimuth [deg]']), reverse=False)
        sortedListTime = sorted(sortedlist, key=lambda row:(row['Time (UTC)']), reverse=False)

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
    search = True
    for key in tiiStats:
        print("Search tii... " + str(key))
        if str(args.tii) in str(key):
            tiiStatsHelper = {args.tii : tiiStats[args.tii] }
            tiiStats = tiiStatsHelper
            print(tiiStatsHelper)
            search = False
            break
        else:
            search = True

    if search:
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
                dataPoint['features'].append(draw_point_transmitter(row['Location'],row['Channel'],tii_row,float(row['Longitude (TX)']),float(row['Latitude (TX)'])))
                LonTx = float(row['Longitude (TX)'])
                LatTx = float(row['Latitude (TX)'])
                CreatePointObj = False
            
            # Define color palette for SNR values
            # Only color the primary received transmitter
            snrColor = "rgba(0, 0, 0, 0)"
            snrColor = snr_colorpalette(float(row['SNR [dB]']),float(row['Level [dB]']))

            if args.primary:
                # Create Receiver point objects, only primary transmitter
                if float(row['Level [dB]']) >= 0.0:
                    dataRxPoint['features'].append(draw_point_receiver(row['Channel'],tii_row,float(row['SNR [dB]']),snrColor,float(row['Longitude (RX)']),float(row['Latitude (RX)'])))
            else:
                # Create Receiver point objects
                dataRxPoint['features'].append(draw_point_receiver(row['Channel'],tii_row,float(row['SNR [dB]']),snrColor,float(row['Longitude (RX)']),float(row['Latitude (RX)'])))

      
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




# Polygon Calculations
azimuthSteps = 0
prevDistance = 0.0
prevAzimuth = 0.0

polyMax = {}

# create dict with default values
i = 0
while i <= 360:
    polyMax.update(
        {
            i: {
                "coordinates": [
                    0.0,
                    0.0
                    ],
                    "distance" : 0.0,
                    "azimuth" : 0.0
                }
        }     
    )
    i = i+10

prev_tii = 0
draw_poly = False

dataPoly2 = {
    "type" : "FeatureCollection",
    "features" : [

    ]
}
coord_array = 0
for tii in tiiStats:
     

    prev_tii = tii
    draw_poly = True

    for azimuth in sortedListPoly:
        tii_row = (int(azimuth['Main']) * 100 + int(azimuth['Sub']))

        if (azimuth['Latitude (TX)'] != '' or azimuth['Longitude (TX)']) and (tii_row == tii):
            aziChannel = azimuth['Channel']
            aziLocation = azimuth['Location']
            aziTxLon = azimuth['Longitude (TX)']
            aziTxLat = azimuth['Latitude (TX)']

            if not (float(azimuth['Azimuth [deg]']) == prevAzimuth):
                # Höchsten Wert ermitteln
                if (float(azimuth['Azimuth [deg]']) >= 0 and float(azimuth['Azimuth [deg]']) < 10):
                    #print("0 to 10 degrees")
                    #print(float(azimuth['Azimuth [deg]']))
                    if polyMax[0]['distance'] <= float(row['Distance [km]']):
                        polyMax.update(
                            {
                                0: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }
                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 10 and float(azimuth['Azimuth [deg]']) < 20):
                    #print("11 to 20 degrees")
                    #print(float(azimuth['Azimuth [deg]']))
                    if polyMax[10]['distance'] <= float(azimuth['Distance [km]']):
                        polyMax.update(
                            {
                                10: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }
                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 20 and float(azimuth['Azimuth [deg]']) < 30):
                    #print("21 to 30 degrees")
                    #print(float(azimuth['Azimuth [deg]']))
                    if polyMax[20]['distance'] <= float(azimuth['Distance [km]']):
                        polyMax.update(
                            {
                                20: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }
                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 30 and float(azimuth['Azimuth [deg]']) < 40):
                    #print("31 to 40 degrees")
                    #print(float(azimuth['Azimuth [deg]']))
                    if polyMax[30]['distance'] <= float(azimuth['Distance [km]']):
                        polyMax.update(
                            {
                                30: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }
                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 40 and float(azimuth['Azimuth [deg]']) < 50):
                    #print("40° - 50°")
                    #print("Azimuth: " + azimuth['Azimuth [deg]'])
                    #print("Distance: " + azimuth['Distance [km]']) 
                    #print(float(azimuth['Distance [km]']))
                    # Speicher Distance und winkel im Objekt und rufe sie hier erneut ab
                    # Wenn neue Distance größer als alte, update Objekt
                    if polyMax[40]['distance'] <= float(azimuth['Distance [km]']):
                            polyMax.update(
                                {
                                    40: {
                                        "coordinates": [
                                            float(azimuth['Longitude (RX)']),
                                            float(azimuth['Latitude (RX)'])
                                            ],
                                            "distance" : float(azimuth['Distance [km]']),
                                            "azimuth" : float(azimuth['Azimuth [deg]'])
                                        }
                                }     
                            )
                elif (float(azimuth['Azimuth [deg]']) >= 50 and float(azimuth['Azimuth [deg]']) < 60):
                    if polyMax[50]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                50: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 60 and float(azimuth['Azimuth [deg]']) < 70):
                    if polyMax[60]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                60: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 70 and float(azimuth['Azimuth [deg]']) < 80):
                    if polyMax[70]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                70: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 80 and float(azimuth['Azimuth [deg]']) < 90):
                    if polyMax[80]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                80: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 90 and float(azimuth['Azimuth [deg]']) < 100):
                    if polyMax[90]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                90: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 100 and float(azimuth['Azimuth [deg]']) < 110):
                    if polyMax[100]['distance'] <= float(azimuth['Distance [km]']):    
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                100: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 110 and float(azimuth['Azimuth [deg]']) < 120):
                    if polyMax[110]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                110: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 120 and float(azimuth['Azimuth [deg]']) < 130):
                    if polyMax[120]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                120: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 130 and float(azimuth['Azimuth [deg]']) < 140):
                    if polyMax[130]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                130: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 140 and float(azimuth['Azimuth [deg]']) < 150):
                    if polyMax[140]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                140: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 150 and float(azimuth['Azimuth [deg]']) < 160):
                    if polyMax[150]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                150: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 160 and float(azimuth['Azimuth [deg]']) < 170):
                    if polyMax[160]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                160: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 170 and float(azimuth['Azimuth [deg]']) < 180):
                    if polyMax[170]['distance'] <= float(azimuth['Distance [km]']):
                        #print("41 to 50 degrees")
                        polyMax.update(
                            {
                                170: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 180 and float(azimuth['Azimuth [deg]']) < 190):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                180: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 190 and float(azimuth['Azimuth [deg]']) < 200):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                190: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 200 and float(azimuth['Azimuth [deg]']) < 210):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                200: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 210 and float(azimuth['Azimuth [deg]']) < 220):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                210: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 220 and float(azimuth['Azimuth [deg]']) < 230):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                220: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 230 and float(azimuth['Azimuth [deg]']) < 240):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                230: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 240 and float(azimuth['Azimuth [deg]']) < 250):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                240: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 250 and float(azimuth['Azimuth [deg]']) < 260):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                250: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 260 and float(azimuth['Azimuth [deg]']) < 270):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                260: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 270 and float(azimuth['Azimuth [deg]']) < 280):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                270: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 280 and float(azimuth['Azimuth [deg]']) < 290):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                280: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 290 and float(azimuth['Azimuth [deg]']) < 300):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                290: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 300 and float(azimuth['Azimuth [deg]']) < 310):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                300: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 310 and float(azimuth['Azimuth [deg]']) < 320):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                310: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 320 and float(azimuth['Azimuth [deg]']) < 330):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                320: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 330 and float(azimuth['Azimuth [deg]']) < 340):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                330: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 340 and float(azimuth['Azimuth [deg]']) < 350):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                340: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )
                elif (float(azimuth['Azimuth [deg]']) >= 350 and float(azimuth['Azimuth [deg]']) < 360):
                    if polyMax[180]['distance'] <= float(azimuth['Distance [km]']):
                        #print("180° - 190°")
                        polyMax.update(
                            {
                                350: {
                                    "coordinates": [
                                        float(azimuth['Longitude (RX)']),
                                        float(azimuth['Latitude (RX)'])
                                        ],
                                        "distance" : float(azimuth['Distance [km]']),
                                        "azimuth" : float(azimuth['Azimuth [deg]'])
                                    }

                            }     
                        )


            prevDistance = float(azimuth['Distance [km]'])
            prevAzimuth = float(azimuth['Azimuth [deg]'])


    ## Part where the polygon is created
    i = 0
    while i <= 360:
        if (polyMax[i]['distance'] == 0.0):
            # Fill empty slices with transmitter Data
            polyMax.update(
                {
                    i: {
                        "coordinates": [
                            float(aziTxLon),
                            float(aziTxLat)
                            ],
                            "distance" : 0.0,
                            "azimuth" : 0.0
                        }
                }     
            )
        i = i+10

    ## Create the dataset
    # Put Transmitter info
    dataPoly2['features'].append(
        {
            "type" : "Feature",
            "properties": {
                "Transmitter" : aziLocation,
                "Channel": aziChannel,
                "Tii": tii
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [

                    ]
                ]
            }
        }
    )

    # Put coordinates for polygon
    # repeat first coords to close the polygon
    i = 0
    while i <= 360:

        dataPoly2['features'][coord_array]['geometry']['coordinates'][0].append(
            [
                polyMax[i]['coordinates'][0],
                polyMax[i]['coordinates'][1]
            ]
        )

        i = i + 10

    dataPoly2['features'][coord_array]['geometry']['coordinates'][0].append(
        [
            polyMax[0]['coordinates'][0],
            polyMax[0]['coordinates'][1]
        ]
    )
    
    coord_array = coord_array +1

    # Reset dict
    i = 0
    while i <= 360:
        polyMax.update(
            {
                i: {
                    "coordinates": [
                        0.0,
                        0.0
                        ],
                        "distance" : 0.0,
                        "azimuth" : 0.0
                    }
            }     
        )
        i = i+10

# Put all objects into one main object
data['features'].extend(dataPoint['features'])
data['features'].extend(dataRxPoint['features'])
#data['features'].extend(dataLine['features'])
data['features'].extend(dataPoly2['features'])

# Save Geo json file
# If one tii is selected, tii id will be put into filename
with open(jsonFile, 'w') as file:
    json.dump(data, file, indent=4)
