import os
import sys
import h5py
import numpy as np
import time
import cv2

prefix = 'cxic0415_png_'

label_size = 11
h = 1480.0
w = 1552.0
delta_per = 1

print('loading dataset...')
g = h5py.File(prefix+'idx.h5', 'r')
print('dataset loaded successfully')

set_names = ['val', 'test', 'train']

label_w = 1.0 * label_size / w
label_h = 1.0 * label_size / h


for set_name in set_names:
    print(set_name)
    xys = g['dataset/' + set_name + '/xys']
    _, d, n = xys.shape
    count = 0
    last_per = 0
    t0 = time.time()
    for u in range(n):
        txt = open('cs231n/' + set_name + '/' + str(u).zfill(6) + '.txt', 'w')
        for v in range(d):
            x, y = xys[:,v,u]
            if x+y < 0.001:
                break
            x /= 1.0*w
            y /= 1.0*h
            line = '0 {} {} {} {}\n'.format( x, y, label_w, label_h )
            txt.write(line)
        txt.close()
        count += 1
        per = int( 100 * count / n )
        if per - last_per >= delta_per:
            last_per = per
            t1 = time.time()
            eta = 0.1 * int( 10 * (t1-t0) / count * (n-count) )
            print('{}% ({}/{}) done, {}s to go...'.format( per, count, n, eta ) ) 

g.close()
print('labels built successfully')

