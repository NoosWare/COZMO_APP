#!/usr/bin/env python3
import os
import sys
import argparse
import asyncio
import noos
import cozmo
import time
from cozmo_code import robot_action
from PIL import Image, ImageDraw
from random import randint


class cozmo_use_noos:
    def __init__(self, noos_class):
        self.robot_ = None
        self.noos_ = noos_class
        self.filename_ = 'noos_example.jpeg'
        self.busy_ = False
        self.actions = robot_action(None)
        self.cubes = 0
        self.loop_ = True
        self.cubes_id = []
        cozmo.connect_with_tkviewer(self.run)
        cozmo.connect(self.run)

    async def new_image(self):
        image = self.robot_.world.latest_image
        if image is not None:
            raw_image = image.raw_image
            raw_image.save(self.filename_)
            result = self.noos_.object_recognition(self.filename_)
            if result is not None:
                print(result)
                await self.robot_.say_text(result).wait_for_completed()
                await self.actions.write_text(result)
                await self.robot_.say_text("Is it correct?").wait_for_completed()
            else:
                await self.actions.write_text("ERROR")
                print("\033[91m Error calling Noos Platform \033[0m")
                print("\033[93m Check that your user and password are correct \033[0m \n")
                sys.exit(1)
        else:
            print('No image')

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


    async def cube_tapped(self, evt, obj=None, tap_count=None, **kw):
        if self.busy_ == False and obj.object_id == self.cubes_id[0]:
            self.busy_ = True
            self.actions.cube_lights(obj.object_id, cozmo.lights.green_light)
            await self.new_image()
        elif self.busy_ == True and obj.object_id == self.cubes_id[0]:
            #the reply is correct
            await self.robot_.play_anim_trigger(self.actions.good_anim_list[randint(0,4)]).wait_for_completed()
            self.busy_ = False
            self.actions.cube_lights(obj.object_id, cozmo.lights.blue_light)
        elif self.busy_ == True and obj.object_id == self.cubes_id[1]:
            #the reply is incorrect
            await self.robot_.play_anim_trigger(self.actions.sad_anim_list[randint(0,4)]).wait_for_completed()
            self.busy_ = False
            self.actions.cube_lights(self.cubes_id[0], cozmo.lights.blue_light)
        elif self.busy_ == False and obj.object_id == self.cubes_id[1]:
            #finish program
            print('Finish program')
            await self.robot_.say_text("Bye bye!").wait_for_completed()
            self.loop_ = False
        else:
            return 
        await self.robot_.set_head_angle(cozmo.util.Angle(degrees=10), duration=1.0, in_parallel=True).wait_for_completed()

    
if __name__ == '__main__':
    # Construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--user", required=True,
                    help="Your username")
    ap.add_argument("-p", "--password", required=True,
                    help="Your password")
    args = vars(ap.parse_args())
    
    # Create noos object and pass it to COZMO
    noos_c = noos.noos_class(args['user'], args['password'])
    cozmo_use_noos(noos_c)
