import json
from math import sqrt
import re
import numpy as np

w = 1552
h = 1480

def loadLabels(path, num):
    data = []
    for u in range(num):
        labels = []
        txt = open( path + str(u).zfill(6) + ".txt", 'r').readlines()
        for v, line in enumerate(txt):
            vals = line.split(" ")
            x = round( w * float(vals[1]))
            y = round( h * float(vals[2]))
            labels.append( (x,y) )
        data.append( labels )
    return data

def loadResults(filename):
    print(filename)
    peaks = json.loads( open(filename).read() )
    data = {}
    for u, peak in enumerate(peaks):
        pid = peak["image_id"]
        if pid in data:
            pass
        else:
            data[pid] = []
        data[pid].append( {'bbox':peak['bbox'], 'score':peak['score']} )
    return data

def readStream(filename):
    txt = open(filename, 'r').readlines()
    data = []
    for i, line in enumerate(txt):
        if "/min_fs" in line:
            det = {}
            # print(line)
            vals = line.split(' = ')
            det["min_fs"] = int( vals[1].rstrip() )
        if "/min_ss" in line:
            # print(line)
            vals = line.split(' = ')
            det["min_ss"] = int( vals[1].rstrip() )
        if "/max_fs" in line:
            # print(line)
            vals = line.split(' = ')
            det["max_fs"] = int( vals[1].rstrip() )
        if "/max_ss" in line:
            # print(line)
            vals = line.split(' = ')
            det["max_ss"] = int( vals[1].rstrip() )
        if "/fs" in line:
            # print(line)
            result = re.split(r'([+\/-][\d\.]+)', line)
            det["fs"] = ( round(float(result[1])), round(float(result[3])) )
        if "/ss" in line:
            # print(line)
            result = re.split(r'([+\/-][\d\.]+)', line)
            det["ss"] = ( round(float(result[1])), round(float(result[3])) )
        if "/corner_x" in line:
            # print(line)
            vals = line.split(' = ')
            det["corner_x"] = float( vals[1].rstrip() )
        if "/corner_y" in line:
            # print(line)
            vals = line.split(' = ')
            det["corner_y"] = float( vals[1].rstrip() )
        if "/coffset" in line:
            # print(line)
            vals = line.split(' = ')
            det["coffset"] = float( vals[1].rstrip() )
            data.append( det )
    return data

def cheetah2Det( stream_data, xys, thresh=0.1 ):
    # test format of xys
    if type(xys[0]) is tuple:
        xys2 = xys.copy()
    else:
        xys2 = []
        for xy in xys:
            if xy["score"] > thresh:
                xys2.append(
                    (xy["bbox"][0]+0.5*xy["bbox"][2], xy["bbox"][1]+0.5*xy["bbox"][3] ) )
    new_xys = []
    for x, y in xys2:
        for asic in stream_data:
            if x >= asic["min_fs"] and x <= asic["max_fs"]:
                pass
            else:
                continue
            if y >= asic["min_ss"] and y <= asic["max_ss"]:
                pass
            else:
                continue
            x = x % 194
            y = y % 185
            # xp = asic["corner_x"]
            # yp = asic["corner_y"]
            if asic["fs"][0] == 1:
                xp = x + asic["corner_x"]
            elif asic["fs"][0] == -1:
                xp = -x + asic["corner_x"]
            elif asic["ss"][0] == 1:
                xp = y + asic["corner_x"]
            elif asic["ss"][0] == -1:
                xp = -y + asic["corner_x"]
            if asic["fs"][1] == 1:
                yp = x + asic["corner_y"]
            elif asic["fs"][1] == -1:
                yp = -x + asic["corner_y"]
            elif asic["ss"][1] == 1:
                yp = y + asic["corner_y"]
            elif asic["ss"][1] == -1:
                yp = -y + asic["corner_y"]
            new_xys.append( (xp+0.5, yp+0.5) )
            break
    return new_xys

def drawAsic( stream_data, img ):
    asics = []
    ss_len = 185
    fs_len = 194
    for asic in stream_data:
        my_img = np.flipud(
            img[asic["min_ss"]:(asic["max_ss"]+1),asic["min_fs"]:(asic["max_fs"]+1)],
            )
        if asic["fs"][0] == 1:
            x1 = asic["corner_x"]
            x2 = x1 + fs_len
            t = 0
        elif asic["fs"][0] == -1:
            x2 = asic["corner_x"]
            x1 = x2 - fs_len
            t = 2
        elif asic["ss"][0] == 1:
            x1 = asic["corner_x"]
            x2 = x1 + ss_len
            t = 3
        elif asic["ss"][0] == -1:
            x2 = asic["corner_x"]
            x1 = x2 - ss_len
            t = 1
        if asic["fs"][1] == 1:
            y1 = asic["corner_y"]
            y2 = y1 + fs_len
        elif asic["fs"][1] == -1:
            y2 = asic["corner_y"]
            y1 = y2 - fs_len
        elif asic["ss"][1] == 1:
            y1 = asic["corner_y"]
            y2 = y1 + ss_len
        elif asic["ss"][1] == -1:
            y2 = asic["corner_y"]
            y1 = y2 - ss_len
        asics.append( {"img":np.rot90(my_img,t), "extend":(x1,x2,y1,y2)} )
    return asics




def IOU( x1, y1, w1, h1, x2, y2, w2, h2):
    box1 = ( x1-w1/2.0, y1-h1/2.0, x1+w1/2.0, y1+h1/2.0)
    box2 = ( x2-w2/2.0, y2-h2/2.0, x2+w2/2.0, y2+h2/2.0)
    xA = max( box1[0], box2[0] )
    xB = min( box1[2], box2[2] )
    yA = max( box1[1], box2[1] )
    yB = min( box1[3], box2[3] )

    w = (xB-xA)
    h = (yB-yA)

    #if interArea <= 0: return 0
    if w <= 0 or h <= 0: return 0

    interArea = h * w
    areaA = (box1[2]-box1[0]) * (box1[3]-box1[1])
    areaB = (box2[2]-box2[0]) * (box2[3]-box2[1])
    return interArea / (areaA+areaB-interArea)

def distance( x1, y1, x2, y2 ):
    return sqrt( (x1-x2)**2 + (y1-y2)**2 )
