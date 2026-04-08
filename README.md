# abracadabra tii heatmapper
Tool, that visualizes the tii recordings of the Abracadabra DAB+ program.

## Usage
```python3 tii-heatmapper.py --csv <abracadabra tii csv file>```

## Options
**--csv** CSV file with tii informations, recorded by Abracadabra in the tii section \
**--tii** Limit the processing to only one tii. Format is 0000, so *Main 30* and *Sub 1* will be written as 3001 \
**--tiilist** Lists all tii IDs in a CSV file 
**--primary** Only draw points of the primary received transmitter. This way a proper heatmap of a SFN is drawn

JSON files will be stored in the same folder as the CSV files. If one tii is selected, the tii ID will be attached to the filename.

The output are Geo-JSON files, that can be viewed in editors like https://geojson.io/next/

In an SFN, like Bundesmux 5C, the heatmap is only drawn in color for the transmitter with the strongest signal incoming. Additional transmitters received are drawn in grey colors. This is a limitation of measuring signals in an SFN. But it gives a glimpse of which transmitter covers which area before another transmitter takes over.

Polygons, drawn as coverage estimate, are pretty jittery at the moment.
