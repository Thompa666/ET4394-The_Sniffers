import re
import os
import csv
import argparse
import fileinput
import threading
import time
import pyshark

#Provide data on channel distribution,
#channel sizes and PHY types (a/b/g/n/etc.)
#Which channels are used mostly and by whom
#@Campus, @Dorm, @Street, etc.

#/* https://github.com/wireshark/wireshark/blob/master/wiretap/wtap.h
# * PHY types.
# */
#define PHDR_802_11_PHY_UNKNOWN        0 /* PHY not known */
#define PHDR_802_11_PHY_11_FHSS        1 /* 802.11 FHSS */
#define PHDR_802_11_PHY_11_IR          2 /* 802.11 IR */
#define PHDR_802_11_PHY_11_DSSS        3 /* 802.11 DSSS */
#define PHDR_802_11_PHY_11B            4 /* 802.11b */
#define PHDR_802_11_PHY_11A            5 /* 802.11a */
#define PHDR_802_11_PHY_11G            6 /* 802.11g */
#define PHDR_802_11_PHY_11N            7 /* 802.11n */
#define PHDR_802_11_PHY_11AC           8 /* 802.11ac */
#define PHDR_802_11_PHY_11AD 9 /* 802.11ad */

# global definitions
DEFAULT_BUFFERED_PACKETS = 5
DEFAULT_RESULTS_FILE_NAME = 'results.csv'

# command line parameters
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
fieldnames = ['Channel', 'PHY','PHY_FULL_NAME']
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

        # only interrested in beacon frames for PHY and channel size data.
        if(int(packet.wlan.fc_type) == 0 and int(packet.wlan.fc_subtype) == 8):
            #very dirty hack to get the correct layer
            # packet object contains two attibutes named wlan.......
            #[<RADIOTAP Layer>, <WLAN_RADIO Layer>, <WLAN Layer>, <WLAN Layer>]
            if(len(packet.layers) == 4):
                # https://www.semfionetworks.com/blog/wireshark-how-to-check-if-a-data-frame-is-sent-using-80211n
                #For HT (High Throughput or 802.11n), you can find the information in the
                #beacon frame under "IEEE 802.11 Wireless LAN management frame /
                #Tagged Parameters / Tag: HT Capabilities (802.11n D1.10) / HT Capabilities Info".
                #If the second bit is equal to 1, this would mean that the AP transmitter supports
                # both 20MHz and 40MHz operations.
                if(hasattr(packet.layers[3], 'vht_op_channelwidth')):
                    print '802.11ac', packet.layers[3].vht_op_channelwidth.showname

                #For VHT (Very High Throughput or 802.11ac), you can also find the information
                #in the beacon frame under "IEEE 802.11 Wireless LAN management frame /
                #Tagged Parameters / Tag: VHT Operations (IEEE Std. 802.11ac/D3.1) / VHT Operation Info".
                #You should see a field named: Channel Width.
                elif(hasattr(packet.layers[3], 'ht_capabilities_width')):
                    if(int(packet.layers[3].ht_capabilities_width) == 1):
                        print '802.11n 40mhz'
                    else:
                        print '802.11n 20mhz'
                else:
                    if(int(packet.radiotap.channel_flags_5ghz) == 1):
                         print '802.11a 20mhz' #a router
                    elif(int(packet.radiotap.channel_flags_2ghz) == 1):
                        #todo differentiate b and g routers this below does not work
                        # erp element?
                        if(int(packet.wlan_radio.phy) == 6):
                            print '802.11g' #g router
                        elif (int(packet.wlan_radio.phy) == 4):
                             print '802.11b' #b router

        #print 'Received packet: Channel', packet.wlan_radio.channel,\
        # 'On PHY', packet.wlan_radio.phy.showname

        results_file_writer.writerow((packet.wlan_radio.channel,\
                                        packet.wlan_radio.phy, packet.wlan_radio.phy.showname))


results_file.close()
