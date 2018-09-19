<img src="images/Noos.png" width="200" height="120" />

# COZMO APP

Most of the examples of the NOOS Cloud Platform have been done in C++. However, this doesn't mean that can't be used with other languages.

This repository contains three different games using [NOOS](https://noos.cloud/) and [COZMO](https://www.anki.com/en-gb/cozmo). ![COZMO robot](https://www.stuff.tv/sites/stuff.tv/files/brands/Anki/Cozmo/cozmo-wheelie-e.jpg)

The language used is `Python`

## Before running it

### 1.Prepare your enviroment

The instructions for installing and preparing your enviroment, in case you haven't done it yet, it can be found [here](https://github.com/NoosWare/noos-python-tutorials/blob/master/01._prepare-your-environment.md)

The step `I.2` changes a bit because we need to install more libraries:

```bash
# Install the good python version
pyenv install 3.6.5
# Create an environment 
pyenv virtualenv 3.6.5 noos-python-cozmo
# Activate the environment, the only command you need to remember
# for the next time
pyenv activate noos-python-cozmo
pip install --upgrade pip
# To reach the platform
pip install requests 
# COZMO SDK
pip install  'cozmo[camera]'
pip install  --upgrade cozmo
# Image management library used by cozmo sdk
pip install --user Pillow
```

### 2.Setup your computer for COZMO

The computer will communicate with COZMO via the WIFI that COZMO emits.

Therefore, assuming you already have installed the COZMO Application for Android/iOS in your mobile phone,
you need to read carefully this [documentation](http://cozmosdk.anki.com/docs/initial.html)

## Games

A total of 3 games have been developed. 

### Game 1

The purpose of this one is to show the `object recognition` service.
The game will start when the `blue` cube is pressed. COZMO will make a picture and 
it will say the object with the highest probability that is in the image.
Then, Cozmo will ask if it is correct or not and the game will start again unless 
the `red` cube is pressed.

To run it:

```bash
python3 game1.py -u your_noos_user -p your_password
```

**NOTE**: `Object Recognition` service only recognizes one object in the picture. If there are more object, the result is unknown.

### Game 2

In this case Cozmo will ask for the objects. 
It will ask for 10 objects, if you fail in 1 object you loose.
You can modify the list in the file `game2.py`.

To have enough time to put the object in front of Cozmo, you should press the `blue/green` cube every time the object is prepared.

To finish the program press the `red` cube.

To run it:

```bash
python3 game1.py -u your_noos_user -p your_password
```

**NOTE**: You can find an image of every object in the list for this game in the folder `/images/items`

### Game 3

This game shows the service `ORB`. 
Cozmo will follow the object you indicate. For example, to run it you have to write the following command:

```bash
python3 game1.py -u your_noos_user -p your_password -m False
```

With the option `model` equal to `False`, indicates that you haven't saved a model before. So, when the program starts,
you should press the `blue` cube for taking an image of the object you want to save. After that, Cozmo will try to follow 
the object rotating in the place and moving the head (to avoid Cozmo falls).

In the case you saved the model previously, change the option to `True`. So Cozmo will follow the object without pressing anything.

To finish the program press the `red` cube.

**NOTE:** If you notice that the robot is not following the object you have chosen, modify the value of the `threshold` of the algorithm in `game3.py` file:

```python
async def new_image(...):
    ...
    await self.orb(self.noos_.orb_keypoints(self.filename_, 70))
```

The number is the `threshold`. Do it smaller for filtering better, or bigger if it is not capable of following your object when it's alone (no enviromental noise).
