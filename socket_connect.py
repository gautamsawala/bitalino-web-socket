#!/usr/bin/env python

'''
WebSocket to connect and record from bitalino

Authors: Gautam Sawala & Sifan

'''
import websockets
import asyncio
import json
import threading
from bitclass import bitalino_device
import os
from time import gmtime, strftime
from videoFile import video_file

#bit to be set to 0 to stop recording
keep_recoding = 1

#Users on web socket
USERS = set()
BITALINO = set()
#current_directory = "somethingIsWrong"

@asyncio.coroutine
def register(websocket):
    USERS.add(websocket)

@asyncio.coroutine
def unregister(websocket):
    USERS.remove(websocket)

'Connect to bitalino with the mac-address sent by the button click in server.html'
@asyncio.coroutine
def connect_bitalino(macAddress):
    device_added = 0
    for current_devices in BITALINO:
        if(current_devices.macAddress == macAddress):
            device_added = 1
    
    new_connected_device = bitalino_device(macAddress, 30, 100, 16)
    new_connected_device.connect()
    if new_connected_device.status and not device_added:
        BITALINO.add(new_connected_device)
        message = json.dumps({'type': 'connection_status', 'value': 'success', 'mac': macAddress})
        yield from asyncio.wait([user.send(message) for user in USERS])
        print('added the device with mac: '+new_connected_device.macAddress)
    elif device_added:
        print("device already added with mac: "+ macAddress)
        message = json.dumps({'type': 'connection_status', 'value': 'success', 'mac': macAddress})
        yield from asyncio.wait([user.send(message) for user in USERS])
    else:
        message = json.dumps({'type': 'connection_status', 'value': 'failed', 'mac': macAddress})
        print(USERS)
        yield from asyncio.wait([user.send(message) for user in USERS])
        print('failed to initiate device with mac: '+ macAddress)
        
'Logs the noise in the console. Only works for EDA. 0 -> no noise, repeatetive 1-> noise'
def printNoise():
    threading.Timer(1.0, printNoise).start()
    for bitalino in BITALINO:
        print(bitalino.macAddress+':'+str(bitalino.noise))

'Starts recording from Bitalino and writes to the file, make sure you have output/ folder.'            
def record_from_bitalino():
    global keep_recoding
    global current_directory
    global VIDEO_FILE
    #create a directory everytime the bitalinos are stopped and recorded again.
    current_directory = "output/"+ strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    os.makedirs(current_directory)
    #create a video state file in current directory to log time of playing the videos
    VIDEO_FILE = video_file(current_directory)
    #initiate the bitalino and create the file for respective recording
    for bitalino in BITALINO:
        bitalino.start()
        bitalino.led_on()
        bitalino.create_file(current_directory)  
        
    printNoise()
    # start recording from bitalino and write the results to the file.    
    while(keep_recoding):
        for bitalino in BITALINO:
            sample = bitalino.start_read()
            bitalino.checkNoise(sample)
            sampleString = bitalino.matToString(sample)
            bitalino.write(sampleString)
            #bitalino.checkNoise(sampleString)
    
    #reset the keep_recording bit for next record
    keep_recoding = 1
    #end the recording by closing the file.
    for bitalino in BITALINO:
        bitalino.stop()
        bitalino.led_off()
        bitalino.closeFile()
    
    message = json.dumps({'type': 'record_status', 'value': 'stopped'})
    yield from asyncio.wait([user.send(message) for user in USERS])

'Updates the file with values of which sensor is attached to what input'
def update_sensor_values(value):
    #split the channel values recieved from front end and convert the into string to write to file.
    print(value)
    mac,c0,c1,c2,c3,c4,c5 = value.split("&")
    channels = "time " + "I1 "+ "I2 "+ "O1 "+ "O2 "+ c0+" "+c1+" "+c2+" "+c3+" "+c4+" "+c5+" "
    for bitalino in BITALINO:
        if bitalino.macAddress == mac:
            bitalino.get_sensor_value()
            bitalino.update_sensors(channels)
            print("Channels update for device with mac: "+bitalino.macAddress + " with channel values: "+ channels)
    
    message = json.dumps({'type': 'sensor_update_status', 'value': 'updated'})
    yield from asyncio.wait([user.send(message) for user in USERS])
        
def stop_recording():
    #read the global value of keep_recording and set it to 0 to stop recording. KISS.
    global keep_recoding
    keep_recoding = 0
    #for bitalino in BITALINO:
    #    bitalino.stop()
    message = json.dumps({'type': 'record_status', 'value': 'stopped'})
    yield from asyncio.wait([user.send(message) for user in USERS])
    

#video controls    

def load_video(video_id):
    print(video_id)
    message = json.dumps({'type': 'video_state', 'value': 'loaded', 'id': video_id})
    print(message)
    yield from asyncio.wait([user.send(message) for user in USERS])

def play_video(video_id):
    #global VIDEO_FILE
    #VIDEO_FILE.writeState(video_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Play")
    message = json.dumps({'type': 'video_state', 'value': 'playing', 'id': video_id})
    print(message)
    yield from asyncio.wait([user.send(message) for user in USERS])

def pause_video(video_id):
    #global VIDEO_FILE
    #VIDEO_FILE.writeState(video_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Pause")
    message = json.dumps({'type': 'video_state', 'value': 'stopped', 'id': video_id})
    print(message)
    yield from asyncio.wait([user.send(message) for user in USERS])
    

def playing_video(video_id, timePosition):
    global VIDEO_FILE
    VIDEO_FILE.writeState(video_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Play", timePosition)
    message = json.dumps({'type': 'video_state', 'value': '', 'id': video_id})
    yield from asyncio.wait([user.send(message) for user in USERS])

def pausing_video(video_id, timePosition):
    global VIDEO_FILE
    VIDEO_FILE.writeState(video_id, strftime("%Y-%m-%d %H:%M:%S", gmtime()), "Pause", timePosition)
    message = json.dumps({'type': 'video_state', 'value': '', 'id': video_id})
    yield from asyncio.wait([user.send(message) for user in USERS])
    
#socket control to initiate, trigger and start recording from bitalino
# Port 6888    
def socket_control(websocket, path):
    yield from register(websocket)
    try:
        while True:
            message = yield from websocket.recv()
            data = json.loads(message)
            #print(data)
            if data['action'] == 'connect':
                    #send macAddress to function with data['value']
                    yield from connect_bitalino(data['value'])
            if data['action'] == 'start_read':
                    yield from record_from_bitalino()
    finally:
        yield from unregister(websocket)

#socket control to stop recording from bitalino and update sensor values
# Port 6889 
def socket_control_1(websocket, path):
    yield from register(websocket)
    try:
        while True:
            message = yield from websocket.recv()
            data = json.loads(message)
            #print(data)
            if data['action'] == 'stop_read':
                #stop recording from bitalino
                yield from stop_recording()
            if data['action'] == 'update_sensor':
                yield from update_sensor_values(data['value'])
    finally:
        yield from unregister(websocket)

#socket control to play/pause and control videos
# Port 6890 
def socket_control_3(websocket, path):
    yield from register(websocket)
    try:
        while True:
            message = yield from websocket.recv()
            data = json.loads(message)
            if data['action'] == 'load_video':
                yield from load_video(data['value'])
            if data['action'] == 'play_video':
                yield from play_video(data['value'])
            if data['action'] == 'pause_video':
                yield from pause_video(data['value'])
            if data['action'] == 'video_playing':
                yield from playing_video(data['id'], data['value'])
            if data['action'] == 'video_paused':
                yield from pausing_video(data['id'], data['value'])
    finally:
        yield from unregister(websocket)
        

        
def thread_1():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(websockets.serve(socket_control, 'localhost', 6888))
    asyncio.get_event_loop().run_forever()

def thread_2():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(websockets.serve(socket_control_1, 'localhost', 6889))
    asyncio.get_event_loop().run_forever()
    
def thread_3():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(websockets.serve(socket_control_3, 'localhost', 6890))
    asyncio.get_event_loop().run_forever()
    
websocket_1 = threading.Thread(name="thread_1", target=thread_1)
websocket_2 = threading.Thread(name="thread_2", target=thread_2)
websocket_3 = threading.Thread(name="thread_3", target=thread_3)


websocket_1.start()
websocket_2.start()
websocket_3.start()