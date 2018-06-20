import os
import sys
import h5py
import numpy as np
import time
import cv2

np.random.seed(231)

prefix = 'cxic0415_png_'
n_val = 1000
n_test = 1000
delta_per = 1
thresh = 10000
png = False
idx = True
filelist = sys.stdin.read()
#filelist = 'yolo_data_list.txt'

filenames = filelist.split()
#filenames = open(filelist).read().split()

total_hits = 0
total_peaks = 0

img = None

for filename in filenames:
    print(filename)
    f = h5py.File(filename, 'r')
    nPeaks = f["entry_1/result_1/nPeaks"]
    dataset_hits = len(nPeaks)
    print('hits: ' + str(dataset_hits))
    total_hits += dataset_hits
    dataset_peaks = np.sum(nPeaks)
    print('peaks: ' + str(dataset_peaks))
    total_peaks += dataset_peaks
    if img == None:
        img = f["entry_1/data_1/data"]
        _, h, w = img.shape
    f.close()

print('total hits: ' + str(total_hits))
print('total peaks: ' + str(total_peaks))
print('img:', h, w)


if n_val < 1:
    n_val = int( n_val * total_hits )
if n_test < 1:
    n_test = int( n_test * total_hits )

n_train = total_hits - n_val - n_test

if n_train < 1:
    raise Exception('size of training set should > 1')

print('train data: ' + str(n_train) )
print('val data:   ' + str(n_val) )
print('test data:  ' + str(n_test) )

time.sleep(5)

try:
    g.close()
except:
    pass

if idx:
    print('initializing dataset...')
    g = h5py.File(prefix+'idx.h5', 'w')

    # VAL
    print('initializing VAL set...')
    g_xys = g.create_dataset('dataset/val/xys', (2, 2048, n_val), dtype=int, chunks=(2,2048,100))
    g_origin = g.create_dataset('dataset/val/origin', (2, n_val), dtype=int, chunks=(2,100))

    # TEST
    print('initializing TEST set...')
    g_xys = g.create_dataset('dataset/test/xys', (2, 2048, n_test), dtype=int, chunks=(2,2048,100))
    g_origin = g.create_dataset('dataset/test/origin', (2, n_test), dtype=int, chunks=(2,100))

    # TRAIN
    print('initializing TRAIN set...')
    g_xys = g.create_dataset('dataset/train/xys', (2, 2048, n_train), dtype=int, chunks=(2,2048,100))
    g_origin = g.create_dataset('dataset/train/origin', (2, n_train), dtype=int, chunks=(2,100))

    g_table = g.create_dataset('table', (3, total_hits), dtype=int, chunks=(3,100))

    g.close()
    print('dataset initialized successfully')

print('shuffling...')
rand_idx = np.random.permutation(total_hits)

if idx:
    g = h5py.File(prefix+'idx.h5', 'r+')
    g_table = g['table']
    g_val_xys = g['dataset/val/xys']
    g_test_xys = g['dataset/test/xys']
    g_train_xys = g['dataset/train/xys']
    g_val_origin = g['dataset/val/origin']
    g_test_origin = g['dataset/test/origin']
    g_train_origin = g['dataset/train/origin']

count = 0
last_per = 0
t0 = time.time()
for i, filename in enumerate(filenames):
    print(filename)
    f = h5py.File(filename, 'r')
    if png:
        data = f['entry_1/data_1/data']
	mask = f['entry_1/data_1/mask']
    x = f['entry_1/result_1/peakXPosRaw']
    y = f['entry_1/result_1/peakYPosRaw']
    n = x.shape[0]
    #h = data.shape[1]
    for u in range(n):
        ridx = rand_idx[count]
        if ridx < n_val:
            offset = 0
            if idx:
                g_val_xys[0,:,ridx] = x[u,:]
                g_val_xys[1,:,ridx] = y[u,:]
		g_val_origin[:,ridx] = [i,u]
                g_table[:,count] = [0,i,u]
            if png:
                img = data[u,:,:] * (1-mask[u,:,:,])
                #img[ img < 0 ] = 0
                img *= (255.0/thresh)
                cv2.imwrite('cs231n/val/' + '{}.png'.format(str(ridx-offset).zfill(6)), img)
        elif ridx < n_val+n_test:
            offset = n_val
            if idx:
                 g_test_xys[0,:,ridx-offset] = x[u,:]
                 g_test_xys[1,:,ridx-offset] = y[u,:]
		 g_test_origin[:,ridx-offset] = [i,u]
            if png:
                 img = data[u,:,:] * (1-mask[u,:,:,])
                 #img[ img < 0 ] = 0
                 img *= (255.0/thresh)
                 cv2.imwrite('cs231n/test/' + '{}.png'.format(str(ridx-offset).zfill(6)), img)
        else:
            offset = n_val+n_test
            if idx:
                g_train_xys[0,:,ridx-offset] = x[u,:]
                g_train_xys[1,:,ridx-offset] = y[u,:]
		g_train_origin[:,ridx-offset] = [i,u]
            if png: 
                img = data[u,:,:] * (1-mask[u,:,:,])
                #img[ img < 0 ] = 0
                img *= (255.0/thresh)
                cv2.imwrite('cs231n/train/' + '{}.png'.format(str(ridx-offset).zfill(6)), img)
        count += 1
        per = int( 100 * count / total_hits )
        if per - last_per >= delta_per:
            t1 = time.time() - t0
            eta = 0.1 * int( 10 * t1 / count * (total_hits-count) )
            print( str(per) + '% done (' + str(count) + '/' + str(total_hits) + ')')
            print(str(eta) + 's to go...')
            last_per = per


    f.close()

g.close()
if png:
    print('PNG dataset built successfully')
if idx:
    print('IDX dataset built successfully')

