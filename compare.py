from utils import *

def compare( imgs, results, thresh=0.4, label_size=(7,7), verbose=False ):
    data = {}
    count = 0
    n = 0
    m = 0
    label_w, label_h = label_size
    for u, labels in enumerate(imgs):
        n += len(labels)
        if verbose:
            print("image", u)
        for v, label in enumerate(labels):
            if verbose:
                print("peak", v)
            best_iou = -1
            best_dist = float('inf')
            best_id = -1
            x, y = label
            for w, peak in enumerate(results[u]):
                if peak["score"] < thresh:
                    continue
                if v == 0:
                    m += 1
                x_res = peak["bbox"][0] + 0.5*peak["bbox"][2]
                y_res = peak["bbox"][1] + 0.5*peak["bbox"][3]
                my_iou = IOU( x, y, label_w, label_h,
                    x_res, y_res, peak["bbox"][2], peak["bbox"][3] )
                if my_iou <= 0:
                    continue
                my_dist = distance( x, y, x_res, y_res )
                if my_dist < best_dist:
                    best_dist = my_dist
                    best_iou = my_iou
                    best_id = w
            if best_id == -1:
                if verbose:
                    print("no match")
                    pass
            else:
                if verbose:
                    print("best IOU", best_iou)
                    print("best dist", best_dist)
                data[(u,v)] = (best_iou, best_dist, best_id)
                count += 1

    # STATSTICS

    if count > 0:
        sensitivity = 1.0*count / n
        precision = 1.0*count / m
    else:
        sensitivity = -1
        precision = -1

    overall_iou = 0
    overall_dist = 0

    for key in data:
        val = data[key]
        overall_iou += val[0]
        overall_dist += val[1]

    if count > 0:
        overall_iou /= count
        overall_dist /= count

    stats = ( sensitivity, precision, overall_iou, overall_dist )
    return data, stats
