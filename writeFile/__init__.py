import re
from time import gmtime, strftime

class bitFile(object):
    def __init__(self, macAddress, acqChannels, samplingRate, attSensors):
        self.macAddress = macAddress
        self.acqChannels = acqChannels
        self.samplingRate = samplingRate
        self.attSensors = attSensors
        
    def createFile(self, current_directory):
        print('here')
        filename = str(current_directory)+"/PyBitSignals_" + re.sub(':', '', self.macAddress) + ".txt"
        outputFile = open(filename, "w")
        
        # Write a header to output file
        outputFile.write("# This data is acquired using the BITalino Python API.\n")
        outputFile.write("# The script that recorded this data is written by Sifan Ye.\n")
        outputFile.write("# Note that this is not the same as the output from OpenSignals.\n")
        outputFile.write("# Note that all data written in this file is RAW! (Read 'RAW' like Gordon Ramsay)\n")
        outputFile.write("# Device MAC Address: " + self.macAddress + "\n")
        outputFile.write("# Date and time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        outputFile.write("# Monitored Channels: " + str(self.acqChannels) + "\n")
        outputFile.write("# Sampling Rate: " + str(self.samplingRate) + "\n")
        outputFile.write("# Attached Sensors: " + str(self.attSensors) + "\n")
        outputFile.write("# End of header\n")
        return outputFile