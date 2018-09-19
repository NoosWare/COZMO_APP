#!/usr/bin/env python3

import asyncio
import cozmo
import time
from PIL import Image, ImageDraw
from random import randint
from cozmo.objects import LightCube1Id, LightCube2Id
from cozmo.util import degrees
                

def cozmo_show_image_face(filename, robot, duration):
    image = Image.open(filename)
    resized_image = image.resize(cozmo.oled_face.dimensions(), Image.NEAREST)
    new_image = cozmo.oled_face.convert_image_to_screen_data(resized_image,
                                                             invert_image=True)
    robot.display_oled_face_image(new_image, duration * 1000.0)

class robot_action:
    def __init__(self, robot = None):
        self.robot_ = robot
        self.image_filename_ = "images/noos.png"
        self.cubes = None
        self.fov_x = 0
        self.fov_y = 0
        self.max_angle_head = 44.0
        self.min_angle_head = 0
        self.gif = oled_animation("images/frame_", 9, ".gif")
        self.good_anim_list = [cozmo.anim.Triggers.CodeLabHappy,
                          cozmo.anim.Triggers.CodeLabCelebrate,
                          cozmo.anim.Triggers.CodeLabPartyTime,
                          cozmo.anim.Triggers.CodeLabReactHappy,
                          cozmo.anim.Triggers.CodeLabWin]

        self.sad_anim_list = [cozmo.anim.Triggers.CodeLabUnhappy,
                         cozmo.anim.Triggers.CodeLabFrustrated,
                         cozmo.anim.Triggers.CodeLabBored,
                         cozmo.anim.Triggers.CodeLabYuck,
                         cozmo.anim.Triggers.CodeLabLose]

    @property
    def robot(self):
        return self.robot_

    @robot.setter
    def robot(self, robot_value):
        self.robot_ = robot_value
        self.robot_.camera.image_stream_enabled = True
        self.robot_.camera.color_image_enabled = True
        self.fov_x = self.robot_.world.robot.camera.config.fov_x.degrees
        self.fov_y = self.robot_.world.robot.camera.config.fov_y.degrees
        self.cubes = cozmo_cubes(robot_value)

    async def show_noos(self):
        if self.robot_ is not None:
            cozmo_show_image_face(self.image_filename_, self.robot_, 2)
            await self.robot_.set_head_angle(cozmo.util.Angle(degrees=40), duration=2.0, in_parallel=True).wait_for_completed()
            await self.robot_.set_head_angle(cozmo.util.Angle(degrees=10), duration=1.0, in_parallel=True).wait_for_completed()
            self.cubes.start_lights()
        else:
            print('\033[95m No robot configured \033[0m')
            return

    async def write_text(self, text):
        text_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))
        context = ImageDraw.Draw(text_image)
        context.text((10, 10), text, fill=(255, 255, 255, 255))
        oled_face_data = cozmo.oled_face.convert_image_to_screen_data(text_image)
        self.robot_.display_oled_face_image(oled_face_data, 1500)
        await asyncio.sleep(2)

    def cube_lights(self, id_cube, color):
        self.cubes.change_light(id_cube, color)

    def get_cubes_id(self):
        return [self.cubes.cube1_id, self.cubes.cube2_id]

    def do_animation(self):
        self.gif.show_animation(self.robot_)
        time.sleep(0.5)

    def angle_calculator(self, coordinates):
        #size of the image 320 x 240 pixels
        angle = [0, 0]
        angle[0] = ((coordinates['x'] * self.fov_x / 320) - self.fov_x / 2) * (-1)
        angle[1] = ((coordinates['y'] * self.fov_y / 240) - self.fov_y / 2) * (-1)
        #Limitations of the angle head
        if angle[1] > self.max_angle_head:
            angle[1] = self.max_angle_head
        elif angle[1] < self.min_angle_head:
            angle[1] = self.min_angle_head
        return angle

    async def follow_obj(self, coordinates):
        await self.robot_.turn_in_place(degrees(self.angle_calculator(coordinates)[0])).wait_for_completed()
        await self.robot_.set_head_angle(cozmo.util.Angle(degrees=self.angle_calculator(coordinates)[1]), 
                                                          duration = 0.5,
                                                          in_parallel=True).wait_for_completed()

class cozmo_cubes:
    def __init__(self, robot = None):
        self.robot_ = robot
        self.cube1 = 0
        self.cube2 = 0
        self.cube1_id = 0
        self.cube2_id = 0

    def start_lights(self):
        if self.robot_ is not None:
            self.cube1 = self.robot_.world.get_light_cube(LightCube1Id)
            self.cube2 = self.robot_.world.get_light_cube(LightCube2Id)
            if self.cube1 is not None:
                self.cube1.set_lights(cozmo.lights.blue_light)
                self.cube1_id = self.cube1.object_id 
            else:
                cozmo.logger.warning("Cozmo is not connected to a LightCube1Id cube - check the battery.")
                return

            if self.cube2 is not None:
                self.cube2.set_lights(cozmo.lights.red_light)
                self.cube2_id = self.cube2.object_id
            else:
                cozmo.logger.warning("Cozmo is not connected to a LightCube2Id cube - check the battery.")
                return
        else:
            print('\033[95m No robot configured \033[0m')
            return

    def change_light(self, cube_id, color):
        if cube_id == self.cube1.object_id:
            self.cube1.set_lights(color)
        elif cube_id == self.cube2.object_id:
            self.cube2.set_lights(color)

    def turn_off_lights(self):
        self.cube1.set_lights(cozmo.lights.off_lights)
        self.cube2.set_lights(cozmo.lights.off_lights)

class oled_animation:
    def __init__(self, filename, frames, img_format):
        self.base_name = filename
        self.num_frames = frames
        self.format = img_format

    def show_animation(self, robot):
        for i in range(self.num_frames):
            name = self.base_name + str(i) + self.format
            cozmo_show_image_face(name, robot, 0.2)
            time.sleep(0.2)

