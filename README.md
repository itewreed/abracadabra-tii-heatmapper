# abracadabra tii heatmapper
Tool, that visualizes the tii recordings of the Abracadabra DAB+ program.

# CSV Concatenation
As of Abracadabra release 4.1.0, also the scanner tool is capable of recording enough information to generate heatmaps. The column structure differs from tii recording. So why not unify them? This is what the tii_concatenate tool does. It creates unified csv files, for each frequency one. It works directory wise. So all scans ever done, regardles whether using tii recording, or scanner tool, can be put into one folder. The tool then reads all csv files and creates new csv files, for each freqwuency one file. \
Those files then can be converted to GeoJSON using tii-heatmapper

## Usage
```python3 tii_csv_concatenate.py --inputdir <csv log folder> --outputdir <outputfolder>```

# Heatmap 

## Usage
```python3 tii-heatmapper.py --csv <abracadabra tii csv file>```

## Options
**--csv** CSV file with tii informations, recorded by Abracadabra in the tii section \
**--tii** Limit the processing to only one tii. Format is 0000, so *Main 30* and *Sub 1* will be written as 3001 \
**--tiilist** Lists all tii IDs in a CSV file \
**--primary** Only draw points of the primary received transmitter. This way a proper heatmap of a SFN is drawn

JSON files will be stored in the same folder as the CSV files. If one tii is selected, the tii ID will be attached to the filename.

The output are Geo-JSON files, that can be viewed in editors like https://geojson.io/next/

In an SFN, like Bundesmux 5C, the heatmap is only drawn in color for the transmitter with the strongest signal incoming. Additional transmitters received are drawn in grey colors. This is a limitation of measuring signals in an SFN. But it gives a glimpse of which transmitter covers which area before another transmitter takes over.

# Web viewer
The web viewer is a simple html file using leaflet and some javascript to display transmitters, reception data and coverage areas.
It loads transmitter infos, coverage and reception data as three separate GeoJSON files.
The map layer can be changed to display either the standard OSM, or a topographic map.
Transmitter, reception and coverage layers are selectable. When clicking on a transmitter, the coverage of the transmitter and an info is shown.

The Leaflet-AJAX plugin is used to load GeoJSON data, https://github.com/calvinmetcalf/leaflet-ajax
