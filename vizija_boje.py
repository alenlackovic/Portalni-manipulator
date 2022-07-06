import cv2
import numpy as np

def prepoznavanje_boje(slika_originalna, slika_hsv, donja_granica_hsv, gornja_granica_hsv):
    broj = 1
    provjera_ima_li_boje = 0
    slika_maska = cv2.cvtColor(slika_originalna, cv2.COLOR_BGR2GRAY) * 0
    matrica = np.empty((0, 3), int)

    for kolicina_boja in range(len(donja_granica_hsv)):
        #slika_filtrirana preko slika_hsv prikazuje crnom bojom sve ne određene boje crnom, a određene boje bijelo
        slika_filtrirana = cv2.inRange(slika_hsv, donja_granica_hsv[kolicina_boja], gornja_granica_hsv[kolicina_boja])
        rubovi, hijerarhija = cv2.findContours(slika_filtrirana, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #slika_rubova = cv2.drawContours(slika_originalna, rubovi, -1, (0, 255, 0), 3)
        #slika_filtrirana

        for boja in rubovi:
            if 10000 < cv2.contourArea(boja) < 20000:
                slika_rubova = cv2.drawContours(slika_originalna, boja, -1, (0, 255, 0), 3)
                M = cv2.moments(boja)
                sredista = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                cv2.circle(slika_originalna, sredista, 3, (0, 255, 0), -1)
                sredista = np.append(sredista, kolicina_boja)
                matrica = np.append(matrica, [sredista], axis = 0)
                provjera_ima_li_boje = 1
        if provjera_ima_li_boje != 0:
            broj = broj + 1
        slika_maska = slika_maska + slika_filtrirana


    return slika_originalna, slika_maska, matrica #, slika_rubova