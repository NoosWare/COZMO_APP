#!/usr/bin/env python3

import cv2 

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
 
def average_vector(vector, lenght):
    print(lenght)
    img = cv2.imread('noos_orb_example.jpeg')
    avg = {'x': 0, 'y': 0}
    for keypoint in vector:
        avg['x'] += keypoint['x']
        avg['y'] += keypoint['y']
        center = (int(keypoint['x']), int(keypoint['y']))
        img2 = cv2.circle(img, center, 1, (0,255,0), 0)
    avg['x'] = avg['x'] / lenght
    avg['y'] = avg['y'] / lenght
    img2 = cv2.circle(img2, (int(avg['x']), int(avg['y'])), 2, (0,0,255), -1)
    cv2.imwrite('noos_orb.jpg', img2)
    return avg
