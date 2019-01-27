import random
import os

arr = []
for x in range(2,32,2):
    for y in range(2,32,2):
        for z in range(2,16,2):
            for a in range(2,16,2):
                arr.append((x,y,z,a))

while len(arr) > 0:
    arridx = random.randint(0,len(arr)-1)
    x,y,z,a = arr[arridx]
    filecheck = f'outputs/output_{x}_{y}_{z}_{a}.png'
    if os.path.exists(filecheck) == True:
        print(f"skipping existing file '{filecheck}'.")
    else:
        oscmd=f'python opencv.py {x} {y} {z} {a}'
        print(f'execute: {oscmd}')
        os.system(oscmd)

    arr.remove(arr[arridx])
