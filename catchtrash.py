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
HSV_LOWER = np.array([0, 19, 101])
HSV_UPPER = np.array([21, 255, 255])
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
    trash_items = []
    spawn_timer = 0

    state = STATE_START
    score = 0
    lives = 3
#loop
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
#start
        if state == STATE_START:
            cv2.putText(display, "CATCH THE TRASH", 
                        (win_w // 2 - 290, win_h // 2 - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 165, 255), 3)
            cv2.putText(display, "Hindari Ikan! Tangkap Sampah!",
                        (win_w // 2 - 250, win_h // 2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(display, "PRESS SPACE TO START",
                        (win_w // 2 - 190, win_h // 2 + 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
#gameplay
        elif state == STATE_PLAY:
            if hand_x is not None and hand_y is not None:
                cam_w, cam_h = frame.shape[1], frame.shape[0]
                hook_x = int(hand_x * (win_w / cam_w))
                hook_y = int(hand_y * (win_h / cam_h))
            spawn_timer += 1
    #spwn ikan
            if spawn_timer % 60 == 0:
                fish_type = random.choice([0, 1, 2])
                fish_y = random.randint(250, win_h - 50)
                speed = random.uniform(1, 3)
                fishes.append({
                    'asset': fish_assets[fish_type],
                    'x': -50,                     # mulai kiri
                    'y': fish_y,
                    'speed': speed,
                    'radius': fish_radii[fish_type],
                    'type': fish_type
                })
    #spawn smaph
            if spawn_timer % 120 == 0 and len(trash_items) < 4:
                    trash_items.append({
                        'asset': random.choice(trash_assets),
                        'x': random.randint(100, win_w - 50),
                        'y': random.randint(300, win_h - 50),
                        'radius': 20
                    })
    # ikan keluar 
            for fish in fishes:
                fish['x'] += fish['speed']
            fishes = [f for f in fishes if f['x'] < win_w + 50]
    #collison hook vs sampah
            surviving_trash = []
            for t in trash_items:
                    dist = math.sqrt((hook_x - t['x'])**2 + (hook_y - t['y'])**2)
                    if dist < t['radius'] + 15:  
                        score += 10
                    else:
                        surviving_trash.append(t)
            trash_items = surviving_trash
    #collison hook vs ikan
            surviving_fishes = []
            hit_fish = False
            for f in fishes:
                dist = math.sqrt((hook_x - f['x']) ** 2 + (hook_y - f['y']) ** 2)
                if dist < f['radius'] + 15 and not hit_fish:
                    lives -= 1
                    hit_fish = True
                    if lives <= 0:
                        state = STATE_GAMEOVER
                else:
                    surviving_fishes.append(f)
            fishes = surviving_fishes 
                
    #sampah
            for t in trash_items:
                chroma_key_overlay(display, t['asset'], 
                                t['x'] - 20, t['y'] - 20, win_w, win_h)
    #ikan
            for f in fishes:
                aw, ah = f['asset'].shape[1], f['asset'].shape[0]
                chroma_key_overlay(display, f['asset'],
                                  int(f['x'])-aw//2, int(f['y'])-ah//2,
                                  win_w, win_h)
    #perahu
            boat_x = (win_w - boat.shape[1]) // 2
            boat_y = 30
            chroma_key_overlay(display, boat, boat_x, boat_y, win_w, win_h)
    #tali pancing
            rod_tip_x = boat_x + boat.shape[1] - 70
            rod_tip_y = boat_y + boat.shape[0] * 0.35
            cv2.line(display, (int(rod_tip_x), int(rod_tip_y)),
                    (hook_x, hook_y), (200, 200, 200), 2)
    #hook
            chroma_key_overlay(display, hook, hook_x - hook.shape[1]//2, hook_y - hook.shape[0]//2, win_w, win_h)
    #scor hati
            cv2.putText(display, f"SCORE: {score}", (win_w - 200, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            for i in range(lives):
                chroma_key_overlay(display, hati_ui,
                                win_w - 200 + i*40, 50,
                                win_w, win_h)
#gameover
        elif state == STATE_GAMEOVER:
            cv2.putText(display, "GAME OVER",
                        (win_w // 2 - 225, win_h // 2 - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 3)
            cv2.putText(display, f"FINAL SCORE: {score}",
                        (win_w // 2 - 200, win_h // 2 + 20),                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 2)
            cv2.putText(display, "PRESS R TO RESTART",
                        (win_w // 2 - 170, win_h // 2 + 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
# PIP
        pip_w, pip_h = 160, 120
        mask_resized = cv2.resize(hand_mask, (pip_w, pip_h))
        mask_3ch = cv2.cvtColor(mask_resized, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(display, (10, 10), (10 + pip_w, 10 + pip_h), 
                    (255, 255, 255), 2)
        display[10:10+pip_h, 10:10+pip_w] = mask_3ch
        
        cv2.imshow("Catch the Trash", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            if state == STATE_START:
                state = STATE_PLAY
                score = 0
                lives = 3
                fishes = []
                trash_items = []
                spawn_timer = 0
        elif key == ord('r'):
            if state == STATE_GAMEOVER:
                state = STATE_START
                score = 0
                lives = 3
                fishes = []
                trash_items = []
                spawn_timer = 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
