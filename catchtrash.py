import cv2
import numpy as np
import random
import math

# Konfigurasi
ASSETS_DIR = "assets"
STATE_START = 0
STATE_PLAY = 1
STATE_GAMEOVER = 2

#hsv
HSV_LOWER = np.array([0, 50, 50])
HSV_UPPER = np.array([20, 255, 255])
MORPH_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

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
#bgr hsv
def detect_hand(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, MORPH_KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, MORPH_KERNEL)
#centroid
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy, mask
    return None, None, mask
    
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

# resize
    hook_h, hook_w = hook.shape[:2]
    target_hook_w = 40
    hook = cv2.resize(hook, (target_hook_w, int(hook_h * (target_hook_w / hook_w))))

    boat_h, boat_w = boat.shape[:2]
    boat = cv2.resize(boat, (int(boat_w * 0.4), int(boat_h * 0.4)))

    fish_small_h, fish_small_w = fish_small.shape[:2]
    fish_small = cv2.resize(fish_small, (90, int(fish_small_h * (90 / fish_small_w))))
    fish_medium_h, fish_medium_w = fish_medium.shape[:2]
    fish_medium = cv2.resize(fish_medium, (60, int(fish_medium_h * (60 / fish_medium_w))))
    fish_big_h, fish_big_w = fish_big.shape[:2]
    fish_big = cv2.resize(fish_big, (90, int(fish_big_h * (90 / fish_big_w))))

    target_trash_w = 40
    h1, w1 = kaleng1.shape[:2]
    kaleng1 = cv2.resize(kaleng1, (target_trash_w, int(h1 * (target_trash_w / w1))))
    h2, w2 = kaleng2.shape[:2]
    kaleng2 = cv2.resize(kaleng2, (target_trash_w, int(h2 * (target_trash_w / w2))))

    hati_ui = cv2.resize(hati_img, (30, 30))
#random
    fish_assets = [fish_small, fish_medium, fish_big]
    trash_assets = [kaleng1, kaleng2]
 #rad collison
    fish_radii = [45, 30, 50] 

    fishes = []

#loop
    spawn_timer = 0
    hook_x, hook_y = 400, 300  # Nilai default posisi kail
    
#cam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    cv2.namedWindow("Catch the Trash", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Catch the Trash", 800, 600)

    while True:
        # windows resize
        rect = cv2.getWindowImageRect("Catch the Trash")
        win_w, win_h = rect[2], rect[3]
        if win_w <= 0 or win_h <= 0:
            win_w, win_h = 800, 600
            
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # mirror 
        blurred = cv2.GaussianBlur(frame, (5, 5), 1.0)
        hand_x, hand_y, hand_mask = detect_hand(blurred)
        
        display = cv2.resize(bg, (win_w, win_h)).copy()

        spawn_timer += 1

        if spawn_timer % 60 == 0:
            fish_type = random.choice([0, 1, 2])
            fish_y = random.randint(250, win_h - 50)
            speed = random.uniform(1, 3)
    
            fishes.append({
                'asset': fish_assets[fish_type],
                'x': -50,                     # mulai dari luar kiri
                'y': fish_y,
                'speed': speed,
                'radius': fish_radii[fish_type],
                'type': fish_type
            })
        
        chroma_key_overlay(display, boat, 300, 50, win_w, win_h)
        
        # ikan spwn
        for fish in fishes:
            fish['x'] += fish['speed']
            chroma_key_overlay(display, fish['asset'], int(fish['x']), int(fish['y']), win_w, win_h)
        fishes = [f for f in fishes if f['x'] < win_w + 50]

        chroma_key_overlay(display, kaleng1, 500, 250, win_w, win_h)
        chroma_key_overlay(display, kaleng2, 600, 350, win_w, win_h)
        chroma_key_overlay(display, hati_ui, 50, 50, win_w, win_h)

        if hand_x is not None and hand_y is not None:
            cam_w, cam_h = frame.shape[1], frame.shape[0]
            hook_x = int(hand_x * (win_w / cam_w))
            hook_y = int(hand_y * (win_h / cam_h))

        #hook
        chroma_key_overlay(display, hook, hook_x - hook.shape[1]//2, hook_y - hook.shape[0]//2, win_w, win_h)
            
# PIP
        pip_w, pip_h = 160, 120
        mask_resized = cv2.resize(hand_mask, (pip_w, pip_h))
        mask_3ch = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(display, (10, 10), (10 + pip_w, 10 + pip_h), 
                    (255, 255, 255), 2)
        display[10:10+pip_h, 10:10+pip_w] = mask_3ch
        
        cv2.imshow("Catch the Trash", display)
        cv2.imshow("Original", frame)
        cv2.imshow("Mask", hand_mask)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
