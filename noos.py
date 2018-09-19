#!/usr/bin/env python3

import requests
import json
import sys

class noos_class:
    def __init__(self, user, psw):
        self.header = {
            'User-Token': user,
            'Accept-Token': psw
        }

    def send_post(self, filename, url, json_data = None):
        # The form to submit
        if json_data is not None:
            print(json.dumps(json_data))
            files = {
                'json': (None, json.dumps(json_data), 'application/json'),
                'filename': (filename, open(filename, 'rb'))
            }
        else:
            files = {
                'filename': (filename, open(filename, 'rb'))
            }
        try:
            response = requests.post(url, headers = self.header, files = files)
        except requests.exceptions.RequestException as e:  #All request errors
            print('\033[91m', e, '\033[0m')
            return  
        return response.json()

    #Object recognition
    def object_recognition(self, filename): 
        json = self.send_post(filename, 'https://demo.noos.cloud:9001/object_recognition')
        if json is None:
            return 

        if json['error'] == '':
            result = self.obj_result(json)
            if result == '':
                return 'Object not found'
            else:
                return result
        else:
            return json['error']

    def obj_result(self, json):
        max_value = 0
        result = ''
        for i, obj in enumerate(json['result']):
            if (obj['probability'] > max_value):
                max_value = obj['probability']
                result = obj['label']
        return result   

    #ORB
    def keypoints_result(self, json):
        keypoints = []
        for i, keyp in enumerate(json['keypoints']):
            dict = {'x' : keyp['x'], 'y' : keyp['y']}
            keypoints.append(dict)
        return keypoints

    def orb_keypoints(self, filename, threshold):
        json = self.send_post(filename, 
                              'https://demo.noos.cloud:9001/orb_query', 
                              {"model": filename, "theta": threshold})
        if json is None:
            return

        if json['error'] == '':
            result = self.keypoints_result(json)
            if result == '':
                print ('No keypoints')
                return 
            else:
                return result
        else:
            print(json['error'])
            return 

    def add_orb_model(self, filename):
        json = self.send_post(filename, 
                              'https://demo.noos.cloud:9001/orb_add_model', 
                              {"name": filename})
        if json is None:
            return 'No reply'

        if json['error'] == '':
            if json['result'] == False:
                return 'Model has not been saved'
        else:
            return json['error']
        return json['result']


