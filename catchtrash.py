import cv2
import numpy as np
import random
import math

# Konfigurasi global
ASSETS_DIR = "assets"
STATE_START = 0
STATE_PLAY = 1
STATE_GAMEOVER = 2

def load_asset(filename):
    path = ASSETS_DIR + "/" + filename
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Asset tidak ditemukan: {path}")
    return img

def main():
    bg = load_asset("bg_underwater.jpg")
    print(bg.shape)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Tidak bisa membuka webcam")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    cv2.namedWindow("Catch the Trash", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Catch the Trash", 800, 600)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # mirror 

        
        display = cv2.resize(bg, (800, 600)).copy()
        boat_x = 300
        boat_y = 50

        cv2.imshow("Catch the Trash", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
