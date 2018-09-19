#!/usr/bin/env python3
import os
import sys
import argparse
import asyncio
import noos
import cozmo
import time
from common import str2bool, average_vector
from cozmo_code import robot_action
from PIL import Image, ImageDraw
from random import randint


class cozmo_use_noos:
    def __init__(self, noos_class, model_saved):
        self.robot_ = None
        self.noos_ = noos_class
        self.filename_ = 'noos_orb_example.jpeg'
        self.busy_ = False
        self.actions = robot_action(None)
        self.loop_ = True
        self.model_saved_ = model_saved
        self.cubes_id = []
        cozmo.connect_with_tkviewer(self.run)
        cozmo.connect(self.run)

    async def new_image(self, event, *, image:cozmo.world.CameraImage, **kw):
        if self.model_saved_ == True and self.busy_ == False:
            self.busy_ = True
            image = self.robot_.world.latest_image
            if image is not None:
                raw_image = image.raw_image
                raw_image.save(self.filename_)
                await self.orb(self.noos_.orb_keypoints(self.filename_, 70))
            else:
                print('No image')
                self.busy_ = False
                return 'Error'

    async def run(self, coz_conn):
        await self.set_up_event(coz_conn)
        while self.loop_:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)

    async def set_up_event(self, coz_conn):
        asyncio.set_event_loop(coz_conn._loop)
        self.robot_ = await coz_conn.wait_for_robot()
        self.actions.robot = self.robot_
        await self.actions.show_noos()
        self.cubes_id = self.actions.get_cubes_id() 
        self.robot_.world.add_event_handler(cozmo.objects.EvtObjectTapped, self.cube_tapped)
        self.robot_.world.add_event_handler(cozmo.world.EvtNewCameraImage, self.new_image)

    async def cube_tapped(self, evt, obj=None, tap_count=None, **kw):
        if  obj.object_id == self.cubes_id[0] and self.model_saved_ == False:
            await self.save_model()
        elif obj.object_id == self.cubes_id[1]:
            #finish program
            await self.end()    
        else:
            return 

    async def save_model(self):
        image = self.robot_.world.latest_image
        if image is not None:
            raw_image = image.raw_image
            raw_image.save(self.filename_)
            reply = self.noos_.add_orb_model(self.filename_)
            if reply == True:
                self.model_saved_ = True
            else:
                print("\033[91m Error saving model in the cloud: ", reply, "\033[0m")
         
    async def orb(self, keypoints):
        if keypoints is not None:
            if len(keypoints) < 30: 
                await self.robot_.play_anim_trigger(cozmo.anim.Triggers.CodeLabSquint1).wait_for_completed()
                await self.robot_.say_text("I can't see the object!", play_excited_animation = True).wait_for_completed()
            else:
                avg = average_vector(keypoints, len(keypoints))
                await self.actions.follow_obj(avg)
            self.busy_ = False
            return 
        else:
            await self.actions.write_text("ERROR")
            print("\033[91m Error calling Noos Platform \033[0m")
            print("\033[93m Check that your user and password are correct \033[0m \n")
            sys.exit(1)

    async def end(self):
        print('Finish program')
        await self.robot_.say_text("Bye bye!").wait_for_completed()
        self.loop_ = False

   
if __name__ == '__main__':
    # Construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--user", required=True,
                    help="Your username")
    ap.add_argument("-p", "--password", required=True,
                    help="Your password")
    ap.add_argument("-m", "--model_saved", required=True, type=str2bool,
                    help="If the model has been saved previously in the cloud (boolean)")

    args = vars(ap.parse_args())
    
    # Create noos object and pass it to COZMO
    noos_c = noos.noos_class(args['user'], args['password'])
    cozmo_use_noos(noos_c, args['model_saved'])
