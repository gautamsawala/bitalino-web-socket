import websockets
import asyncio
import threading
import time
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import os, errno

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(611)
ax2 = fig.add_subplot(612)
ax3 = fig.add_subplot(613)
ax4 = fig.add_subplot(614)
ax5 = fig.add_subplot(615)
ax6 = fig.add_subplot(616)

def lastlines(hugefile, n, bsize=2048):
    # get newlines type, open in universal mode to find it
    with open(hugefile, 'rU') as hfile:
        if not hfile.readline():
            return  # empty, no point
        sep = hfile.newlines  # After reading a line, python gives us this
    assert isinstance(sep, str), 'multiple newline types found, aborting'

    # find a suitable seek position in binary mode
    with open(hugefile, 'rs') as hfile:
        hfile.seek(0, os.SEEK_END)
        linecount = 0
        pos = 0

        while linecount <= n + 1:
            # read at least n lines + 1 more; we need to skip a partial line later on
            try:
                hfile.seek(-bsize, os.SEEK_CUR)           # go backwards
                linecount += hfile.read(bsize).count(sep) # count newlines
                hfile.seek(-bsize, os.SEEK_CUR)           # go back again
            except IOError:
                if IOError.errno == errno.EINVAL:
                    # Attempted to seek past the start, can't go further
                    bsize = hfile.tell()
                    hfile.seek(0, os.SEEK_SET)
                    linecount += hfile.read(bsize).count(sep)
                    break
                raise  # Some other I/O exception, re-raise
            pos = hfile.tell()

    # Re-open in text mode
    with open(hugefile, 'r') as hfile:
        hfile.seek(pos, os.SEEK_SET)  # our file position from above

        for line in hfile:
            # We've located n lines *or more*, so skip if needed
            if linecount > n:
                linecount -= 1
                continue
            # The rest we yield
            yield line

def tail( f, lines=2000 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 2048
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


def animate(i):
    #graph_file = open('output/2018_07_12_10_22_40/PyBitSignals_201612220128.txt', 'r')
    #graph_data = tail(graph_file, 6) 
    #lines = graph_data.split('\n')
    lines = lastlines('output/2018_07_12_10_22_40/PyBitSignals_201612220128.txt', 20, 2048)
    for line in lines:
        print(str(line))
    #xs = []
    #ys = []
    #for line in lines:
    #    if len(line) > 1:
    #        x, y = line.split(',')
    #        xs.append(int(x))
    #        ys.append(int(y))
    #ax1.clear()
    #ax1.plot(xs, ys)

def plot_graph(i):
    graph_file = open('output/2018_07_12_10_22_40/PyBitSignals_201612220128.txt', 'r')
    graph_data = tail(graph_file, 20) 
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x = line.split('\t')
            print(x)
            #xs.append(int(x))
            #ys.append(int(y))
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax5.clear()
    ax6.clear()
    ax1.plot(xs, ys)    
    ax2.plot(xs, ys)    
    ax3.plot(xs, ys)    
    ax4.plot(xs, ys)    
    ax5.plot(xs, ys)    
    ax6.plot(xs, ys)    


ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()
