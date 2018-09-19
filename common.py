#!/usr/bin/env python3

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
 
def average_vector(vector, lenght):
    avg = {'x': 0, 'y': 0}
    for keypoint in vector:
        avg['x'] += keypoint['x']
        avg['y'] += keypoint['y']
    avg['x'] = avg['x'] / lenght
    avg['y'] = avg['y'] / lenght
    return avg
