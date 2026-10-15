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
    
def chroma_key_overlay(frame, asset, x, y, frame_w, frame_h):
    h, w = asset.shape[:2]  # tinggi & lebar asset
    # clip
    x1 = max(0, x)           
    y1 = max(0, y)
    x2 = min(frame_w, x + w) 
    y2 = min(frame_h, y + h)
    if x2 <= x1 or y2 <= y1: #offset
        return
    src_x1 = max(0, -x)      
    src_y1 = max(0, -y)
    src_x2 = src_x1 + (x2 - x1)  
    src_y2 = src_y1 + (y2 - y1)

    asset_roi = asset[src_y1:src_y2, src_x1:src_x2]
    frame_roi = frame[y1:y2, x1:x2]

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
