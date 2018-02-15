import re
import os
import csv
import argparse
import fileinput
import threading
import time
import pyshark

# global definitions
DEFAULT_BUFFERED_PACKETS = 5
DEFAULT_RESULTS_FILE_NAME = 'results.csv'

# command line paramenters
parser = argparse.ArgumentParser(description='Capture data of intrest using Wireshark')
parser.add_argument('-n','--nbufferred', default=DEFAULT_BUFFERED_PACKETS,type=int,
                   help='Amount of packets to buffer before processing, optional parameter')
parser.add_argument('-r','--result_file', default=DEFAULT_RESULTS_FILE_NAME,
                   help='File to write the results to, default is results.csv')
parser.add_argument('device', metavar='device_name',
                   help='Device to monitor on i.e. monX')


args = parser.parse_args()
interface = args.device

amount_to_buffer = DEFAULT_BUFFERED_PACKETS
if args.nbufferred:
    amount_to_buffer = args.nbufferred

results_file_name = DEFAULT_RESULTS_FILE_NAME
if args.result_file:
    results_file_name = args.result_file

# Starting of program
print 'Started sniffing on', interface

# wireshark capturing
capture = pyshark.LiveCapture(interface=interface)
#capture.sniff(timeout=5)

results_file_exists = os.path.isfile(results_file_name)

# starting with creation of a csv file with certian fieldnames
# if the specified output file already exists do not write header
# otherwise write the header
fieldnames = ['dbm', 'PHY']
results_file = open(results_file_name,"a+")
results_file_writer = csv.writer(results_file)

if results_file_exists:
    print 'Appending to pre-existing output file'
else:
    results_file_writer.writerow(fieldnames)
    print 'Creating new output file'

# Forever buffer packets and then process/print them to the csv
while True:
    #sniff_continuously param amount of packets to collect before stopping.
    received_packets = capture.sniff_continuously(packet_count=amount_to_buffer)

    for packet in received_packets:
        #print 'Just arrived:', packet
        #print packet.wlan.field_names
        #print 'new packet\n\n'
        #packet.pretty_print()
        print 'Received packet: Signal Strength dbm', packet.wlan_radio.signal_dbm,\
         'On PHY', packet.wlan_radio.phy.showname

        results_file_writer.writerow((packet.wlan_radio.signal_dbm,\
                                        packet.wlan_radio.phy.showname))


results_file.close()
