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
    
def IOU( x1, y1, w1, h1, x2, y2, w2, h2):
    box1 = ( x1-w1/2.0, y1-h1/2.0, x1+w1/2.0, y1+h1/2.0)
    box2 = ( x2-w2/2.0, y2-h2/2.0, x2+w2/2.0, y2+h2/2.0)
    xA = max( box1[0], box2[0] )
    xB = min( box1[2], box2[2] )
    yA = max( box1[1], box2[1] )
    yB = min( box1[3], box2[3] )

    w = (xB-xA)
    h = (yB-yA)
    if w <= 0 or h <= 0: return 0
    interArea = h * w
    #if interArea <= 0: return 0

    areaA = (box1[2]-box1[0]) * (box1[3]-box1[1])
    areaB = (box2[2]-box2[0]) * (box2[3]-box2[1])
    return interArea / (areaA+areaB-interArea)
