from time import gmtime, strftime

class video_file(object):
    def __init__(self, current_directory):
        self.current_directory = current_directory
        outputFile = open(current_directory+"/video_logs.txt", "w")
        outputFile.write("# This is the file for Video Logs \n")
        outputFile.write("# Date and time: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
        outputFile.write("Video id \t Time \t State \t Time Position \n")
    
    def writeState(self, video_id, time, state, timePosition):
        outputFile = open(self.current_directory+"/video_logs.txt", "a")
        outputFile.write(video_id+ "\t" + time + "\t\t" + state + "\t" +str(timePosition)+ "\n")
        outputFile.close()