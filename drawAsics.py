import sys
import re
import matplotlib.pyplot as plt
import matplotlib.patches as pat
import matplotlib.lines as mlines

outputPath = "output/"

filename = sys.argv[1]
print(filename)

txt = open(filename, 'r').readlines()

data = []
for i, line in enumerate(txt):
    if "/min_fs" in line:
        det = {}
        print(line)
        vals = line.split(' = ')
        det["min_fs"] = int( vals[1].rstrip() )
    if "/min_ss" in line:
        print(line)
        vals = line.split(' = ')
        det["min_ss"] = int( vals[1].rstrip() )
    if "/max_fs" in line:
        print(line)
        vals = line.split(' = ')
        det["max_fs"] = int( vals[1].rstrip() )
    if "/max_ss" in line:
        print(line)
        vals = line.split(' = ')
        det["max_ss"] = int( vals[1].rstrip() )
    if "/fs" in line:
        print(line)
        result = re.split(r'([+\/-][\d\.]+)', line)
        det["fs"] = ( round(float(result[1])), round(float(result[3])) )
    if "/ss" in line:
        print(line)
        result = re.split(r'([+\/-][\d\.]+)', line)
        det["ss"] = ( round(float(result[1])), round(float(result[3])) )
    if "/corner_x" in line:
        print(line)
        vals = line.split(' = ')
        det["corner_x"] = float( vals[1].rstrip() )
    if "/corner_y" in line:
        print(line)
        vals = line.split(' = ')
        det["corner_y"] = float( vals[1].rstrip() )
    if "/coffset" in line:
        print(line)
        vals = line.split(' = ')
        det["coffset"] = float( vals[1].rstrip() )
        data.append( det )
print(data)

print('# of ASICs:', len(data))

box_ss = 185
box_fs = 194

fig, ax = plt.subplots(1)
for det in data:
    if det["fs"][1] == 1:
        y_cor = det["corner_y"]
        box_y = box_fs
    elif det["fs"][1] == -1:
        y_cor = det["corner_y"]-box_fs
        box_y = box_fs
    elif det["fs"][0] == 1:
        y_cor = det["corner_y"]
        box_y = box_ss
    elif det["fs"][0] == -1:
        y_cor = det["corner_y"]-box_ss
        box_y = box_ss
    if det["ss"][0] == 1:
        x_cor = det["corner_x"]
        box_x = box_ss
    elif det["ss"][0] == -1:
        x_cor = det["corner_x"]-box_ss
        box_x = box_ss
    elif det["ss"][1] == 1:
        x_cor = det["corner_x"]
        box_x = box_fs
    elif det["ss"][1] == -1:
        x_cor = det["corner_x"]-box_fs
        box_x = box_fs

    plt.plot( det["corner_x"], det["corner_y"], 'ks', 'Size', 0.5 )
    rect = pat.Rectangle( (x_cor, y_cor),
        box_x, box_y, color="c", fill=False, linewidth=0.5)
    ax.add_patch(rect)

ax.set_aspect('equal')
plt.xlim([-1000, 1000])
plt.ylim([-1000, 1000])
plt.savefig( outputPath + 'asics.png', bbox_inces='tight', dpi=300)
