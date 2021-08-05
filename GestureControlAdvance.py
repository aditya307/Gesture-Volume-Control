import cv2
import time
import numpy as np
import handTrackModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#######################################
wCam, hCam = 1290, 720
#######################################

pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)

cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(detectionCon=0.7, maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-55.0, None)

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)
while True:
    success, img = cap.read()

    #Find Hand
    img = detector.findHands(img)
    lmList, bBox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:

        # Filter Based on Sizen
        area = (bBox[2]-bBox[0]) * (bBox[3]-bBox[1]) // 100
        print(area)
        if 400 < area < 2000:
            # print("yes")
            #Find Distance bw inex and thumb
            length, img, lineInfo =  detector.findDistance(4, 8, img)
            # print(length)
            # Convert Volume
            # vol = np.interp(length, [20, 180], [minVol,maxVol])
            volBar = np.interp(length,[50,300], [400, 150])
            volPer = np.interp(length,[50,300], [0,100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)


            ### reduce resolution for smoother
            smoothness = 10
            volPer = smoothness * round(volPer/smoothness)

            ###check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            ###if pinky is down set volume
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 8, (0, 0, 255), cv2.FILLED)
                colorVol = (0,255,0)
            else:
                colorVol = (255,0 , 0)


            # print(lmList[4], lmList[8])

            # print(length)

                cv2.circle(img, (lineInfo[4], lineInfo[5]), 8, (0, 0, 255), cv2.FILLED)

    ###drawings
    cv2.rectangle(img, (50, 150), (85,400),(0,0,255), 3)
    cv2.rectangle(img, (50, int(volBar)), (85,400),(0,0,255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, f'Vol: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_PLAIN, 3, colorVol, 3)


    ###framerate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    cv2.imshow("image", img)
    cv2.waitKey(1)