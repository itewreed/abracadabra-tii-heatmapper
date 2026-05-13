import argparse
import csv
import os

header_translation = {
    'Zeit (UTC)': 'Time (UTC)',
    'Kanal': 'Channel',
    'Frequenz [kHz]': 'Frequency [kHz]',
    'UEID': 'UEID',
    'Label': 'Label',
    'SNR [dB]': 'SNR [dB]',
    'Feldstärke [dB]': 'Level [dB]',
    'Standort': 'Location',
    'Leistung [kW]': 'Power [kW]',
    'Entfernung [km]': 'Distance [km]',
    'Azimut [deg]': 'Azimuth [deg]',
    'Breitenkreis (TX)': 'Latitude (TX)',
    'Längenkreis (TX)': 'Longitude (TX)',
    'Breitenkreis (RX)': 'Latitude (RX)',
    'Längenkreis (RX)': 'Longitude (RX)',
}

parser = argparse.ArgumentParser(description='Unify and concatenate CSV files from Abracadabra TII recorder and scanner tool')
parser.add_argument(
    "--inputdir",
    type   =str,
    dest   ="inputdir",
    metavar="Directory with CSV scans",
    default="None",
    help   ="Reads all CSV files in the directory, concatenates by frequency and creates a CSV file for each frequency",
)

parser.add_argument(
    "--outputdir",
    type   =str,
    dest   ="outputdir",
    metavar="Directory for concatenated CSV output",
    default="None",
    help   ="Directory to write the concatenated output to",
)

args = parser.parse_args()

if os.path.isdir(args.inputdir) and os.path.isdir(args.outputdir):
    csvdir = args.inputdir + '/'
    outdir = args.outputdir + '/'
    network = {}
else:
    print(args.inputdir + " or " + args.outputdir + " is not a directory")
    exit(2)


# Reading in CSV File(s)
for csvfile in sorted(os.listdir(csvdir)):
    fullcsvfile = csvdir + csvfile
    
    if os.path.isfile(fullcsvfile):
        with open(fullcsvfile) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
            reader.fieldnames = [header_translation.get(h, h) for h in reader.fieldnames]  # translates header to English
            sortedlist = sorted(reader, key=lambda row:(row['Frequency [kHz]'],row['Main'],row['Sub']), reverse=False)          

            for row in sortedlist:
                frequency = int(row['Frequency [kHz]'])

                if frequency not in network:
                    network[frequency] = {
                        "features" : [
                                [
                                str(row['Channel']),
                                int(row['Frequency [kHz]']),
                                row['Label'],
                                row['SNR [dB]'],
                                row['Main'],
                                row['Sub'],
                                row['Level [dB]'],
                                row['Location'],
                                row['Distance [km]'],
                                row['Azimuth [deg]'],
                                row['Latitude (TX)'],
                                row['Longitude (TX)'],
                                row['Latitude (RX)'],
                                row['Longitude (RX)']
                            ]
                        ]
                    }
                else:
                    network[frequency]['features'].append(
                        [
                            str(row['Channel']),
                            int(row['Frequency [kHz]']),
                            row['Label'],
                            row['SNR [dB]'],
                            row['Main'],
                            row['Sub'],
                            row['Level [dB]'],
                            row['Location'],
                            row['Distance [km]'],
                            row['Azimuth [deg]'],
                            row['Latitude (TX)'],
                            row['Longitude (TX)'],
                            row['Latitude (RX)'],
                            row['Longitude (RX)']
                        ]
                    )     


# Writing Dictionary into CSV files
for channel in network:
    # Open a CSV file to write
    with open(outdir + str(channel) + '.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'Channel',
            'Frequency [kHz]',
            'Label',
            'SNR [dB]',
            'Main',
            'Sub',
            'Level [dB]',
            'Location',
            'Distance [km]',
            'Azimuth [deg]',
            'Latitude (TX)',
            'Longitude (TX)',
            'Latitude (RX)',
            'Longitude (RX)'
            ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=';')
        writer.writeheader()
    
        for feature in network[channel]['features']:
            # Write rows into the file
            writer.writerow(
                {
                    'Channel': feature[0],
                    'Frequency [kHz]': feature[1],
                    'Label': feature[2],
                    'SNR [dB]': feature[3],
                    'Main': feature[4],
                    'Sub': feature[5],
                    'Level [dB]': feature[6],
                    'Location': feature[7],
                    'Distance [km]': feature[8],
                    'Azimuth [deg]': feature[9],
                    'Latitude (TX)': feature[10],
                    'Longitude (TX)': feature[11],
                    'Latitude (RX)': feature[12],
                    'Longitude (RX)': feature[13]
                }
            )