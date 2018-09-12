from bitalino import BITalino
from writeFile import bitFile
from time import gmtime, strftime
from _overlapped import NULL
from cv2.cv2 import compare

class bitalino_device(object):
    def __init__(self, macAddress, batteryThreshold, samplingRate, nSamples):
        self.macAddress = macAddress
        self.batteryThreshold = batteryThreshold
        self.acqChannels = [0,1,2,3,4,5]
        self.samplingRate = samplingRate
        self.nSamples = nSamples
        self.status = 0
        self.ledOn = [1,0]
        self.ledOff = [0,1]
        self.attSensors = "this"
        self.file = ""
        self.threshold = 5
        self.noise = [1,1,1,1,1,1]
        self.prevData = [0,0,0,0,0,0]
    
    def connect(self):
        try:
            self.connection = BITalino(self.macAddress)
            self.status = 1
        except:
            print('failed to connect')
                    
        
    def state(self):
        return self.connection.state()
    
    def start(self):
        self.connection.start(self.samplingRate, self.acqChannels)
        
    def start_read(self):
        return self.connection.read(self.nSamples)
    
    def stop(self):
        self.connection.stop()
        
    def led_on(self):
        self.connection.trigger(self.ledOn)
    
    def led_off(self):
        self.connection.trigger(self.ledOff)
        
    def create_file(self, current_directory):
        print('in create file')
        new_file = bitFile(self.macAddress, self.acqChannels, self.samplingRate, self.attSensors)
        self.file = new_file.createFile(current_directory)

    def update_sensors(self, sensorValues):
        self.attSensors = sensorValues
    
    def get_sensor_value(self):
        print(str(self.attSensors))
      
    def matToString(self, matrix):
        """
        :param matrix: The matrix to be turned into string
        Returns a string of a matrix row by row, without brackets or commas
        """
        r, c = matrix.shape
        string = ""
        for row in range(0,r):
            string = string + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\t"
            for col in range(1,c):
                string = string + str(int(matrix[row,col])) + "\t"
            string += "\n"
        return string  
    
    def openFile(self):
        open(self.file, "w")
    
    def checkNoiseArray(self, channels):
        for i in range(6):
            if(int(channels[i]) - int(self.prevData[i]) < self.threshold):
                self.noise[i] = 0
            else:
                self.noise[i] = 1
        self.prevData = channels
        #print(self.noise)
        
    def checkNoise(self, data):
        data = self.matToString(data)
        #print(data)
        channels_list = data.split('\n')
        
        for channels in channels_list:
            channel  = channels.split('\t')
            if len(channel) > 1:
                self.checkNoiseArray(channel[5:11])
                
        #for channel in channels[2:]:
        #    print(channel)
    
    def write(self, string_sample):
        self.file.write(string_sample)
        
    def closeFile(self):
        self.file.close()