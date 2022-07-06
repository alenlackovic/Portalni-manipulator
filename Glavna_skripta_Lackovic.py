import numpy as np
import cv2
from pypylon import pylon
from vizija_boje import prepoznavanje_boje
from Kalibracija import kalibracija
import glob
import socket

###############################

kalib=0

IP = '192.168.0.1' #definirano u TIA Portalu
port = 2000 #definirano u TIA Portalu
sock=socket.socket()
sock.connect((IP, port)) #povezivanje s uređajem

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
images = glob.glob(r'*.png') #putanja do željenih slika, *.png uzima sve u direktoriju gdje je skripta

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        kamera_rgb = image.GetArray()
        kamera_rgb = cv2.flip(kamera_rgb, -1)

        if kalib == False:
            mapx, mapy, x, y, w, h = kalibracija(kamera_rgb, images)
            kalib = True

        kalibrirana_kamera_rgb = cv2.remap(kamera_rgb, mapx, mapy, cv2.INTER_LINEAR)
        kalibrirana_kamera_rgb = kalibrirana_kamera_rgb[y:y + h, x:x + w]
        kalibrirana_kamera_rgb = kalibrirana_kamera_rgb[0:800, 0:850]

        #Kx = 4,85; Ky = 4,9 # koeficijenti [px/mm] ubačeno i TIA Portalu

        kamera_hsv = cv2.cvtColor(kalibrirana_kamera_rgb, cv2.COLOR_BGR2HSV)  # prebacivanje iz RBG u HSV spektar

        plava_donja_granica_hsv = (90, 110, 70)
        plava_gornja_granica_hsv = (128, 255, 255)
        #zelena_donja_granica_hsv = (32, 70, 30)
        #zelena_gornja_granica_hsv = (70, 255, 255)
        narancasta_donja_granica_hsv = (3, 90, 30)
        narancasta_gornja_granica_hsv = (20, 255, 255)

        HSV_donja_granica = [narancasta_donja_granica_hsv, plava_donja_granica_hsv]
        HSV_gornja_granica = [narancasta_gornja_granica_hsv, plava_gornja_granica_hsv]

        slika_zadnja, slika_maska, matrica = prepoznavanje_boje(kalibrirana_kamera_rgb, kamera_hsv, HSV_donja_granica, HSV_gornja_granica)#[0][1][2]

        cv2.imshow("slika", slika_zadnja)
        cv2.imshow("slika_maska", slika_maska)

        print(matrica)
        data = sock.recv(1)
        matrica_s=matrica

        data_int = int.from_bytes(data, "big")
        print("RECIEVED:", data_int)
        if data_int == 1 and matrica.size != 0:
            saljem = str(matrica_s[0][0]) + " " + str(matrica_s[0][1]) + " " + str(matrica_s[0][2])
            saljem_byte = bytes(saljem, 'utf-8')
            saljem_plc = sock.send(saljem_byte)
            print ("POSLANO:", saljem_byte)

        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
    grabResult.Release()

camera.StopGrabbing()

cv2.destroyAllWindows()