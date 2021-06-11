import pyautogui
import time
import cv2 as cv
import keyboard
import numpy as np
from matplotlib import pyplot as plt
import mss
from PIL import ImageGrab

# Adımlar #
# Bot Kurulumu #
# Kurulum Kontrolu ve Onay #
# Onaylanmışsa Oltayı At #
# Beklemeye başla #
# olta vurunca mini game başlat #
i = 0
idleTime = 0
fishingPosition = {0, 0}
miniGameLeftTop = {0, 0}
miniGameRightBottom = {0, 0}
bobberPosition = {0, 0}
characterPosition = {0, 0}
succesfuly = 'false'
STATUS = 'ıdle'


def oltaAt(x, y, cX, cY):
    time.sleep(2)
    pyautogui.rightClick(cX, cY)
    pyautogui.moveTo(x, y)
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(0.9)
    pyautogui.mouseUp()


# Bilgileri topla
while True:
    time.sleep(0.5)
    print('select the location of your character and press " X "')
    if keyboard.read_key() == 'x':
        characterPosition = pyautogui.position()
        print('character position = ' + str(characterPosition))
        time.sleep(1)
        break
while True:
    time.sleep(0.5)
    print('choose where to cast your fishing rod and press " Q "')
    if keyboard.read_key() == "q":
        fishingPosition = pyautogui.position()
        oltaAt(fishingPosition[0], fishingPosition[1],
               characterPosition[0], characterPosition[1])
        print('fishing position = '+str(fishingPosition))
        time.sleep(1)
        break
while True:
    time.sleep(0.5)
    print('select the bottom of the cork and press " X "')
    if keyboard.read_key() == "x":
        bobberPosition = pyautogui.position()
        while True:
            time.sleep(0.2)
            volume = ImageGrab.grab().getpixel(
                (bobberPosition[0], bobberPosition[1]))
            print(str(volume))
            if volume[0] > 60:
                print('color value too high')
                succesfuly = 'false'
                break
            else:
                print(str(bobberPosition) + ' Succesfuly!')
                succesfuly = 'true'
                break
        if succesfuly == 'true':
            break
        else:
            print('Wrong Position :' + str(volume))
            continue
while True:
    time.sleep(0.5)
    print('when the mini game opens select the top left and press " Q "')
    if keyboard.read_key() == "q":
        miniGameLeftTop = pyautogui.position()
        break
while True:
    time.sleep(0.5)
    print('mini game right bottom " X "')
    if keyboard.read_key() == "x":
        miniGameRightBottom = pyautogui.position()
        with mss.mss() as sct:
            area = {"top": miniGameLeftTop[1], "left": miniGameLeftTop[0], "width": miniGameRightBottom[0] -
                    miniGameLeftTop[0], "height": miniGameRightBottom[1]-miniGameLeftTop[1]}
            img_rgb = np.array(sct.grab(area))
            img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
            cv.imshow('result', img_gray)
            cv.waitKey(0)
            time.sleep(2)
            cv.destroyAllWindows()
        time.sleep(1)
        ask = input('Do you confirm the shown area ? Y/N = ')
        if ask == 'y':
            break
        else:
            continue

# Mini game tespit et


def Detect_Bobber():
    with mss.mss() as sct:
        area = {"top": miniGameLeftTop[1], "left": miniGameLeftTop[0], "width": miniGameRightBottom[0] -
                miniGameLeftTop[0], "height": miniGameRightBottom[1]-miniGameLeftTop[1]}
        center = area["width"]/2
        img_rgb = np.array(sct.grab(area))
        img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
        template = cv.imread('mantar.png', 0)
        w, h = template.shape[::-1]
        res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        state = ""
        cv.waitKey(50)
        #cv.imshow('result', res)
        for pt in zip(*loc[::-1]):
            cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            if(pt[0] > center):
                state = "Right"
            else:
                state = "Left"
            return [True, state]
        return [False, state]


# Botu başlat
if STATUS == 'ıdle':
    ask = input('Do you want to start the bot ? Y/N = ')

    if ask == 'y':
        print('In 5 seconds the bot will start. Press " X " to exit')
        time.sleep(4)
        while True:
            print('Starting Albion Fishing Bot...')
            time.sleep(3)
            i = 0
            idleTime = 0
            STATUS = 'start'
            oltaAt(fishingPosition[0], fishingPosition[1],
                   characterPosition[0], characterPosition[1])
            time.sleep(2)
            while True:
                power = ImageGrab.grab().getpixel(
                    (bobberPosition[0], bobberPosition[1]))

                deger = Detect_Bobber()
                print('power = ' + str(power[0]))
                if STATUS == 'catching':
                    while True:
                        deger = Detect_Bobber()
                        print(deger)
                        if deger[0]:
                            pyautogui.mouseDown()
                            if deger[1] == 'Right':
                                pyautogui.mouseUp()
                            if deger[1] == 'Left':
                                pyautogui.mouseDown()
                        else:
                            i += 1
                            pyautogui.mouseUp()
                            if i > 20:
                                print('Restart Bot')
                                STATUS = 'end'
                                break
                if power[0] > 45 and STATUS != 'end':
                    STATUS = 'catching'
                    print('catching...')
                    pyautogui.leftClick(
                        bobberPosition[0], bobberPosition[1])
                    pyautogui.leftClick()
                if STATUS == 'end':
                    break
                idleTime += 1
                if idleTime > 450:
                    idleTime = 0
                    print('timed out restarting')
                    break

    else:
        print('Exit')
        exit()
