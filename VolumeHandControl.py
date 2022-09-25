import enum
import this

import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import keyboard

# from pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######################
wCam, hCam = 640, 480
######################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
#volume.SetMasterVolumeLevel(-20.0, None)

######  Finger Data ######
I_down, M_down, R_down, P_down = False, False, False, False
##########################


def GetPintPoz(i):
    x, y = lmList[i][1], lmList[i][2]
    return [x, y]


xT= yT = 0  # Thumb
xI= yI = 0  # Index
xM= yM = 0  # Middle
x3= y3 = 0  # Root
x4= y4 = 0  # Index_Root

def ControllVolume():

    if len(lmList) != 0:

        xT, yT = lmList[4][1], lmList[4][2]  # Thumb
        xI, yI = lmList[8][1], lmList[8][2]  # Index
        xM, yM = lmList[12][1], lmList[12][2]  # Middle
        x3, y3 = lmList[0][1], lmList[0][2]  # Root
        x4, y4 = lmList[5][1], lmList[5][2]  # Index_Root

        d_I_M = math.hypot(xI - xM, yI - yM)

        cv2.circle(img, (xT, yT), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (xI, yI), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (xT, yT), (xI, yI), (255, 0, 255))

        size = math.hypot(x3 - x4, y3 - y4)
        length = math.hypot(xT - xI, yT - yI)
        signal = length / size

        vol = np.interp(signal, [0.1, 1.2], [minVol, maxVol])
        volPer = np.interp(signal, [0.1, 1.6], [0, 100])
    # print(vol)
        volume.SetMasterVolumeLevel(vol, None)
        cv2.putText(img, f'vol: {int(volPer)}', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)


angle_I = angle_M = angle_R = angle_P = 0


run = True
while run:
    if keyboard.is_pressed(' '):          # Terminate the program with space bar
        print('Program Terminated!')
        run = False
    
    success, img = cap.read()
    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img, draw=False)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    ControllVolume()

    cv2.imshow("image", img)
    cv2.waitKey(1)
