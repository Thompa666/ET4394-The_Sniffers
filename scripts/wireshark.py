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
DEFAULT_BUFFERED_PACKETS = 50
DEFAULT_CHANNEL_RESULTS_FILE_NAME = 'channel_results.csv'
DEFAULT_BEACON_RESULTS_FILE_NAME = 'beacon_results.csv'

# command line parameters
parser = argparse.ArgumentParser(description='Capture data of intrest using Wireshark')
parser.add_argument('-c','--channel_results_file', default=DEFAULT_CHANNEL_RESULTS_FILE_NAME,
                   help='File to write the channel results to, default is results.csv')
parser.add_argument('-g','--beacon_results_file', default=DEFAULT_BEACON_RESULTS_FILE_NAME,
                    help='File to write the beacon results to, default is results.csv')
parser.add_argument('device', metavar='device_name',
                   help='Device to monitor on i.e. monX')


args = parser.parse_args()
interface = args.device

channel_results_file_name = DEFAULT_CHANNEL_RESULTS_FILE_NAME
if args.channel_results_file:
    channel_results_file_name = args.channel_results_file

beacon_results_file_name = DEFAULT_BEACON_RESULTS_FILE_NAME
if args.beacon_results_file:
    beacon_results_file_name = args.beacon_results_file

# Starting of program
print 'Started sniffing on', interface

# wireshark capturing
capture = pyshark.LiveCapture(interface=interface)

# get the filesready
channel_results_file_exists = os.path.isfile(channel_results_file_name)

# starting with creation of a csv file with certian fieldnames
# if the specified output file already exists do not write header
# otherwise write the header
channel_fieldnames = ['Transmitter_Adress','Channel','PHY', 'Frame_Type','Frame_Subtype']
channel_results_file = open(channel_results_file_name,"a+")
channel_results_file_writer = csv.writer(channel_results_file)

if channel_results_file_exists:
    print 'Appending to pre-existing channel output file'
else:
    channel_results_file_writer.writerow(channel_fieldnames)
    print 'Creating new channel output file'

beacon_results_file_exists = os.path.isfile(beacon_results_file_name)

# starting with creation of a csv file with certian fieldnames
# if the specified output file already exists do not write header
# otherwise write the header
beacon_fieldnames = ['Transmitter_Adress','Channel', 'is_5Ghz','SSID','Channel_Width','PHY_Type']
beacon_results_file = open(beacon_results_file_name,"a+")
beacon_results_file_writer = csv.writer(beacon_results_file)

if beacon_results_file_exists:
    print 'Appending to pre-existing beacon output file'
else:
    beacon_results_file_writer.writerow(beacon_fieldnames)
    print 'Creating new beacon output file'



# Forever buffer packets and then process/print them to the csv

# sniff_continuously param, amount of packets to collect before stopping.
# if the parameter packet_count is given to the function
# a infinite amount of pipes is generated over time in the current version
# of the pyshark code and then the file limit is reached and it crashes.
received_packets = capture.sniff_continuously()

for packet in received_packets:
    # only interrested in beacon frames for PHY and channel size data.
    if(int(packet.wlan.fc_type) == 0 and int(packet.wlan.fc_subtype) == 8):
        #very dirty hack to get the correct layer
        # packet object contains two attibutes named wlan.......
        #[<RADIOTAP Layer>, <WLAN_RADIO Layer>, <WLAN Layer>, <WLAN Layer>]
        if(len(packet.layers) == 4):
            #For VHT (Very High Throughput or 802.11ac), you can also find the information
            #in the beacon frame under "IEEE 802.11 Wireless LAN management frame /
            #Tagged Parameters / Tag: VHT Operations (IEEE Std. 802.11ac/D3.1) / VHT Operation Info".
            #You should see a field named: Channel Width.
            if(hasattr(packet.layers[3], 'vht_op_channelwidth')):
                width = re.findall('\d+', packet.layers[3].vht_op_channelwidth.showname_value)
                if(int(width[0]) == 20 and int(width[1]) == 40):
                    width = '20 or 40'
                else:
                    width = width[0]
                print '802.11ac', width, 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                beacon_results_file_writer.writerow((packet.wlan.ta,\
                    packet.wlan_radio.channel,\
                    packet.radiotap.channel_flags_5ghz,\
                    packet.layers[3].ssid,\
                    width,\
                    8))

            # https://www.semfionetworks.com/blog/wireshark-how-to-check-if-a-data-frame-is-sent-using-80211n
            #For HT (High Throughput or 802.11n), you can find the information in the
            #beacon frame under "IEEE 802.11 Wireless LAN management frame /
            #Tagged Parameters / Tag: HT Capabilities (802.11n D1.10) / HT Capabilities Info".
            #If the second bit is equal to 1, this would mean that the AP transmitter supports
            # both 20MHz and 40MHz operations.
            elif(hasattr(packet.layers[3], 'ht_capabilities_width')):
                if(int(packet.layers[3].ht_capabilities_width) == 1):
                    print '802.11n 40', 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                    beacon_results_file_writer.writerow((packet.wlan.ta,\
                        packet.wlan_radio.channel,\
                        packet.radiotap.channel_flags_5ghz,\
                        packet.layers[3].ssid,\
                        40,\
                        7))
                else:
                    print '802.11n 20', 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                    beacon_results_file_writer.writerow((packet.wlan.ta,\
                        packet.wlan_radio.channel,\
                        packet.radiotap.channel_flags_5ghz,\
                        packet.layers[3].ssid,\
                        20,\
                        7))
            else:
                # If not n on 5ghz then it must be a 802.11a router
                if(int(packet.radiotap.channel_flags_5ghz) == 1):
                    print '802.11a 20', 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                    beacon_results_file_writer.writerow((packet.wlan.ta,\
                        packet.wlan_radio.channel,\
                        packet.radiotap.channel_flags_5ghz,\
                        packet.layers[3].ssid,\
                        20,\
                        5))
                elif(int(packet.radiotap.channel_flags_2ghz) == 1):
                    # https://mrncciew.com/2014/10/08/802-11-mgmt-beacon-frame/
                    # ERP element is present only on 2.4GHz network supporting
                    # 802.11g & it is present in beacon & probe responses.

                    # only g+ has ERP element
                    if(hasattr(packet.layers[3], 'erp_info')):
                        print '802.11g', 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                        beacon_results_file_writer.writerow((packet.wlan.ta,\
                            packet.wlan_radio.channel,\
                            packet.radiotap.channel_flags_5ghz,\
                            packet.layers[3].ssid,\
                            20,\
                            6))
                    else:
                        print '802.11b', 'SSID:', packet.layers[3].ssid, 'transmitter:', packet.wlan.ta
                        beacon_results_file_writer.writerow((packet.wlan.ta,\
                            packet.wlan_radio.channel,\
                            packet.radiotap.channel_flags_5ghz,\
                            packet.layers[3].ssid,\
                            20,\
                            4))

    if(hasattr(packet,'wlan_radio') and hasattr(packet,'wlan')):
        if(hasattr(packet.wlan_radio, 'channel') and \
            hasattr(packet.wlan, 'ta')):
            channel_results_file_writer.writerow((packet.wlan.ta,\
						packet.wlan_radio.channel,\
                                                packet.wlan_radio.phy,\
                                                packet.wlan.fc_type,\
                                                packet.wlan.fc_subtype))


channel_results_file.close()
beacon_results_file.close()
