import pyautogui
import time
import cv2 as cv
import keyboard
import numpy as np
from matplotlib import pyplot as plt
import mss
from PIL import ImageGrab
from enum import Enum
import random
# Adımlar #
# Bot Kurulumu #
# Kurulum Kontrolu ve Onay #
# Onaylanmışsa Oltayı At #
# Beklemeye başla #
# olta vurunca mini game başlat #


miniGameLeftTop = {0, 0}
miniGameRightBottom = {0, 0}

minigame_stop_timer_threshold = 2
red_pixel_threshold = 60
total_red_pixel = {}

fishing_spots = []
fishCount = 0
fishingSpotIndex = 0
fishingSpotIndexStepSign = -1  # 1 or -1
nextCharacterPositionThreshold = 2


characterPosition = {0, 0}
fishingPosition = {0, 0}
bobberPosition = [0, 0]
bobber_feather_area = {}

moveDelay = 0.2


class STATUS (Enum):
    IDLE = 1,
    WAITING = 2,
    END = 3,
    CATCHING = 4,
    MINIGAME = 5,
    RESTARTING = 6


class BOBBER_STATE(Enum):
    NONE = 0,
    LEFT = 1,
    RIGHT = 2


Status = STATUS.IDLE


class FishingSpots:
    characterPosition = {}
    fishingPositions = []
    bobberPositions = []
    bobber_feather_areas = []

    def __init__(self, characterPosition, fishingPositions, bobberPositions, bobber_feather_areas):
        self.characterPosition = characterPosition
        self.fishingPositions = fishingPositions
        self.bobberPositions = bobberPositions
        self.bobber_feather_areas = bobber_feather_areas


def ReGenerateBobberAreaTemplate():
    global total_red_pixel, bobber_feather_area
    offset = 5
    bobber_feather_area = {
        "top": bobberPosition[1]-offset, "left": bobberPosition[0]-offset, "width": offset*2, "height": offset*2}
    img = cv.cvtColor(
        np.array(sct.grab(bobber_feather_area)), cv.COLOR_BGR2GRAY)
    total_red_pixel = np.sum(img > red_pixel_threshold)
    print(total_red_pixel)
    cv.imwrite("bobber_water.PNG", np.array(sct.grab(bobber_feather_area)))
    if total_red_pixel > 20:
        return True, bobber_feather_area
    else:
        return False, bobber_feather_area


def oltaAt(x, y, cX, cY):
    time.sleep(2)
    pyautogui.rightClick(cX, cY)
    time.sleep(moveDelay)
    pyautogui.moveTo(x, y)
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(1)
    pyautogui.mouseUp()
    time.sleep(2)
    if Status != STATUS.IDLE:
        time.sleep(2)
        isRightSpot = ReGenerateBobberAreaTemplate()
        if isRightSpot == False:
            oltaAt(x, y, cX, cY)


# Bilgileri topla
while True:

    characterPosition = {}
    fishingPositions = []
    bobberPositions = []
    bobber_feather_areas = []

    while True:
        time.sleep(0.2)
        print('Select Character Position "q"')
        if keyboard.read_key() == 'q':
            characterPosition = pyautogui.position()
            print('character position = ' + str(characterPosition))
            break
    while True:
        while True:
            time.sleep(0.2)
            print('Select Fishing Coordinate "e"')
            if keyboard.read_key() == "e":
                fishingPosition = pyautogui.position()
                oltaAt(fishingPosition[0], fishingPosition[1],
                       characterPosition[0], characterPosition[1])
                print('fishing position = '+str(fishingPosition))
                fishingPositions.append(fishingPosition)
                break
        while True:
            time.sleep(0.2)
            print('Select Red Bobber Feather "q"')
            if keyboard.read_key() == "q":
                bobberPosition = pyautogui.position()
                with mss.mss() as sct:
                    isRightSpot, area = ReGenerateBobberAreaTemplate()
                    if isRightSpot:
                        bobberPositions.append(bobberPosition)
                        bobber_feather_areas.append(area)
                        break
                    else:
                        print("Select again!!!")
        ask = input('Add new Fishing Coordinate? y/n = ')
        if ask == 'y':
            continue
        else:
            break

    fishing_spots.append(FishingSpots(
        characterPosition, fishingPositions, bobberPositions, bobber_feather_areas))
    ask = input('Add new character position? y/n = ')
    if ask == 'y':
        continue
    else:
        fishingSpotIndex = len(fishing_spots) - 1
        break


while True:
    time.sleep(0.5)
    print('when the mini game opens select the top left and press "q"')
    if keyboard.read_key() == "q":
        miniGameLeftTop = pyautogui.position()
        break

while True:
    time.sleep(0.5)
    print('mini game right bottom " e "')
    if keyboard.read_key() == "e":
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
        ask = input('Do you confirm the shown area ? y/n = ')
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
        state = BOBBER_STATE.NONE
        # cv.waitKey(50)
        for pt in zip(*loc[::-1]):
            cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            if(pt[0] > center):
                state = BOBBER_STATE.RIGHT
            else:
                state = BOBBER_STATE.LEFT
            return [True, state]
        return [False, state]


def Detect_Water_Bobber():
    global detection_threshold
    with mss.mss() as sct:
        water_bobber_img = np.array(sct.grab(bobber_feather_area))
        water_bobber_img_gray = cv.cvtColor(
            water_bobber_img, cv.COLOR_BGR2GRAY)
        red_pixel_count = np.sum(water_bobber_img_gray > red_pixel_threshold)

        if red_pixel_count / total_red_pixel < 0.7:
            print("Bobber Disappear")
            return False
        else:
            return True


def AssignVariables(index):
    global fishing_spots, characterPosition, fishingPosition, bobberPosition, bobber_feather_area
    print(str(index) + "characterPosition" + str(characterPosition))
    characterPosition = fishing_spots[index].characterPosition
    fishingPositionIndex = random.randint(
        0, len(fishing_spots[index].fishingPositions)-1)
    # print ("Index: " + str(index) +" Fishing Spot Count: " +str(len(fishing_spots[index].fishingPositions))
    # +" bobberPosition Count: " +str(len(fishing_spots[index].bobberPositions)) + " fishingPositionIndex: " + str(fishingPositionIndex))
    fishingPosition = fishing_spots[index].fishingPositions[fishingPositionIndex]
    bobberPosition = fishing_spots[index].bobberPositions[fishingPositionIndex]
    bobber_feather_area = fishing_spots[index].bobber_feather_areas[fishingPositionIndex]


# Botu başlat
if Status == STATUS.IDLE:
    ask = input('Do you want to start the bot ? Y/N = ')

    if ask == 'y':
        print('In 2 seconds the bot will start. Press " X " to exit')
        time.sleep(2)
        while True:
            print('Starting Albion Fishing Bot...')
            start_time = time.time()
            Status = STATUS.WAITING

            if fishCount != 0 and fishCount % nextCharacterPositionThreshold == 0:
                fishingSpotIndex += fishingSpotIndexStepSign

                if fishingSpotIndex >= len(fishing_spots):
                    fishingSpotIndexStepSign = -1
                    fishingSpotIndex += fishingSpotIndexStepSign
                elif fishingSpotIndex < 0:
                    fishingSpotIndexStepSign = 1
                    fishingSpotIndex += fishingSpotIndexStepSign
                moveDelay = 3
            else:
                moveDelay = 0.2

            AssignVariables(fishingSpotIndex)

            oltaAt(fishingPosition[0], fishingPosition[1],
                   characterPosition[0], characterPosition[1])

            while True:
                if Detect_Water_Bobber() == False and Status != STATUS.END:
                    Status = STATUS.CATCHING
                    print('Catching...')
                    pyautogui.leftClick(bobberPosition[0], bobberPosition[1])

                if Status == STATUS.CATCHING:
                    fishCount += 1
                    print("Total Fish:" + str(fishCount))
                    minigame_start_time = time.time()
                    while True:
                        isDetecting, state = Detect_Bobber()
                        if isDetecting:
                            minigame_start_time = time.time()
                            pyautogui.mouseDown()
                            if state == BOBBER_STATE.RIGHT:
                                pyautogui.mouseUp()
                            if state == BOBBER_STATE.LEFT:
                                pyautogui.mouseDown()
                        else:
                            pyautogui.mouseUp()
                            if time.time() - minigame_start_time > minigame_stop_timer_threshold:
                                print('Restart Bot')
                                Status = STATUS.END
                                break

                if Status == STATUS.END:
                    break

                if time.time() - start_time > 60:
                    print('Timed out, restaring!!!')
                    Status = STATUS.END
                    break

    else:
        print('Exit')
        exit()
