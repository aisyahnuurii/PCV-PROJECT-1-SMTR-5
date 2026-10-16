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

    # Deteksi background putih 
    lower_white = np.array([240, 240, 240])
    upper_white = np.array([255, 255, 255])
    white_mask = cv2.inRange(asset_roi, lower_white, upper_white)
    non_white_mask = cv2.bitwise_not(white_mask)

    for c in range(3):
        frame_roi[:, :, c] = np.where(
            non_white_mask > 0,
            asset_roi[:, :, c],
            frame_roi[:, :, c]
        )

def main():
    bg = load_asset("bg_underwater.jpg")
    boat = load_asset("boat.jpg")
    hook = load_asset("hook.jpg")
    hati_img = load_asset("hati.jpg")
    
    fish_small = load_asset("fish_small.jpg")
    fish_medium = load_asset("fish_medium.jpg")
    fish_big = load_asset("fish_big.jpg")
    
    kaleng1 = load_asset("kaleng1.png")
    kaleng2 = load_asset("kaleng2.jpg")
#cam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
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
    # windows resize
        rect = cv2.getWindowImageRect("Catch the Trash")
        win_w, win_h = rect[2], rect[3]
        if win_w <= 0 or win_h <= 0:
            win_w, win_h = 800, 600
        
        display = cv2.resize(bg, (win_w, win_h)).copy()
        boat_x = 300
        boat_y = 50

        chroma_key_overlay(display, boat, 300, 50, win_w, win_h)
        chroma_key_overlay(display, hook, 400, 300, win_w, win_h)
        chroma_key_overlay(display, fish_small, 100, 200, win_w, win_h)
        chroma_key_overlay(display, fish_medium, 200, 300, win_w, win_h)
        chroma_key_overlay(display, fish_big, 300, 400, win_w, win_h)
        chroma_key_overlay(display, kaleng1, 500, 250, win_w, win_h)
        chroma_key_overlay(display, kaleng2, 600, 350, win_w, win_h)
        chroma_key_overlay(display, hati_img, 50, 50, win_w, win_h)
        
        cv2.imshow("Catch the Trash", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
