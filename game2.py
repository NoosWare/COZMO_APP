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
        self.objs = words() 
        cozmo.connect_with_tkviewer(self.run)
        cozmo.connect(self.run)

    async def new_image(self):
        image = self.robot_.world.latest_image
        if image is not None:
            raw_image = image.raw_image
            raw_image.save(self.filename_)
            result = self.noos_.object_recognition(self.filename_)
            if result is not None:
                return result
            else:
                await self.actions.write_text("ERROR")
                print("\033[91m Error calling Noos Platform \033[0m")
                print("\033[93m Check that your user and password are correct \033[0m \n")
                sys.exit(1)
        else:
            print('No image')
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


    async def cube_tapped(self, evt, obj=None, tap_count=None, **kw):
        if self.busy_ == False and obj.object_id == self.cubes_id[0]:
            self.busy_ = True
            self.actions.cube_lights(obj.object_id, cozmo.lights.green_light)
            await self.take_word()
        elif self.busy_ == True and obj.object_id == self.cubes_id[0]:
            await self.game()
        elif obj.object_id == self.cubes_id[1]:
            #finish program
            await self.end()    
            return
        else:
            return 
        await self.robot_.set_head_angle(cozmo.util.Angle(degrees=10), duration=1.0, in_parallel=True).wait_for_completed()
        
    async def game(self):
        word_result = await self.new_image()
        correct = self.objs.check_word(word_result, self.objs.word_to_guess)
        if correct == True:
            await self.robot_.say_text("correct!").wait_for_completed()
            self.actions.do_animation()
            await self.actions.write_text("CORRECT!")
            await self.robot_.say_text("Next word will be...").wait_for_completed()
            await self.take_word()
        elif correct == False and self.objs.fail_counter < 5:
            await self.robot_.say_text("No! Try again!").wait_for_completed()
        else:
            await self.robot_.say_text("wrong! End of game").wait_for_completed()
            await self.robot_.play_anim_trigger(self.actions.sad_anim_list[randint(0,6)]).wait_for_completed()
            await self.end()

    async def take_word(self):
        self.objs.decide_obj()
        if self.objs.word_to_guess == "End":
            await self.robot_.say_text("You have tried all the words! You win!").wait_for_completed()
            self.objs.clear()
            await self.robot_.play_anim_trigger(self.actions.good_anim_list[randint(0,6)]).wait_for_completed()
            self.busy_ = False
            return
        await self.robot_.say_text(self.objs.word_to_guess).wait_for_completed()

    async def end(self):
        print('Finish program')
        await self.robot_.say_text("Bye bye!").wait_for_completed()
        self.loop_ = False


class words:
    def __init__(self):
        self.objs_ = ["cat", "chair", "violin",
                      "spider", "television", "clock",
                      "entlebucher"]
        self.rnd_list_ = []
        self.fail_counter = 0
        self.word_to_guess = ""

    def decide_obj(self):
        if len(self.rnd_list_) == 5:
            self.word_to_guess = "End"
            return
        number = randint(0,6)
        if number not in self.rnd_list_:
            self.rnd_list_.append(number)
            print(self.objs_[number])
            self.word_to_guess = self.objs_[number]
            return 
        else:
            self.decide_obj()
        
    def check_word(self, result, word_checker):
        if result is not None:
            words_result = result.split()
            for every_w in words_result:
                word_no_coma = every_w.replace(",", "").lower();
                if word_no_coma == word_checker:
                    self.fail_counter = 0
                    return True
            print("NO MATCH")    
            self.fail_counter += 1
        return False

    def clear(self):
        self.rnd_list_ = []


    
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
