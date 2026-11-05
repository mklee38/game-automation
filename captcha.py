import warnings
# 封鎖所有 PyTorch 觸發的 UserWarning 警告
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

import pyautogui
import cv2
import numpy as np
import easyocr
import time
import os
from collections import Counter

pyautogui.FAILSAFE = True

#print("正在載入 EasyOCR...")
#reader = easyocr.Reader(['en'], gpu=False, quantize=True)
#print("EasyOCR 載入完成\n")

# ==================== 請根據你的 captcha_window.png 修改這四個值 ====================
TARGET_OFFSET_X = 158
TARGET_OFFSET_Y = 30
TARGET_WIDTH    = 85
TARGET_HEIGHT   = 58
# =================================================================================
GAME_WINDOW=(0, 0, 1280, 1000)      # None

MAX_RETRIES = 3

DIGIT_TEMPLATES = {
    '1': 'templates/one.png',
    '2': 'templates/two.png',
    '3': 'templates/three.png',
    '4': 'templates/four.png',
    '5': 'templates/five.png',
    '6': 'templates/six.png',
    '7': 'templates/seven.png',
    '8': 'templates/eight.png',
    '9': 'templates/nine.png',
    '0': 'templates/zero.png',
}

def find_template_topleft(template_path, threshold=0.655, region=GAME_WINDOW):
    if not os.path.exists(template_path):
        print(f"[錯誤] 找不到模板：{template_path}")
        return None

    screenshot = pyautogui.screenshot(region=region)
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    if template is None:
        print(f"[錯誤] 無法讀取：{template_path}")
        return None

    result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        print(f"[匹配成功] {os.path.basename(template_path)} 分數={max_val:.3f} 左上角={max_loc}")
        return max_loc
    else:
        print(f"[匹配失敗] {os.path.basename(template_path)} 最高分數={max_val:.3f}")
        return None


def find_template_center(template_path, threshold=0.655):
    pos = find_template_topleft(template_path, threshold)
    if not pos:
        return None
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    h, w = template.shape[:2]
    return (pos[0] + w // 2, pos[1] + h // 2)


def preprocess_blue_noise_captcha(img_bgr):
    """denoise.py pipeline: ×6 upscale → HSV V → NLMeans h=12"""
    scale = 6
    upscaled = cv2.resize(img_bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    hsv = cv2.cvtColor(upscaled, cv2.COLOR_BGR2HSV)
    v_channel = hsv[:, :, 2]
    denoised = cv2.fastNlMeansDenoising(v_channel, None, h=12)
    return denoised


def ocr_from_relative_area(window_topleft):
    print("正在載入 EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=False, quantize=True)
    print("EasyOCR 載入完成\n")

    left = window_topleft[0] + TARGET_OFFSET_X
    top  = window_topleft[1] + TARGET_OFFSET_Y

    print(f"[裁切] 目標區域：({left}, {top}, {TARGET_WIDTH}x{TARGET_HEIGHT})")
    print("[OCR] 最多擷取 3 張（前兩張相同即提早結束）")

    predictions = []

    for i in range(1, 4):
        crop = pyautogui.screenshot(region=(left, top, TARGET_WIDTH, TARGET_HEIGHT))
        crop_cv = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)

        # Save raw (optional, comment out if you want max speed)
        #cv2.imwrite(f"debug_raw_{i}.png", crop_cv)                         # Screencapture!!! Comment out the cv2.imwrite lines if you want maximum speed.

        # Preprocess
        denoised = preprocess_blue_noise_captcha(crop_cv)
        #cv2.imwrite(f"debug_denoised_{i}.png", denoised)                   # Screencapture!!! Comment out the cv2.imwrite lines if you want maximum speed.

        # OCR + sort left-to-right
        try:
            results = reader.readtext(denoised, detail=1, allowlist='0123456789', mag_ratio=1.5)

            def left_x(bbox):
                return min(point[0] for point in bbox)

            results_sorted = sorted(results, key=lambda r: left_x(r[0]))
            texts = [r[1] for r in results_sorted]
            digits = ''.join(texts).strip()
            print(f"  第{i}張: {texts} → '{digits}'")

            if len(digits) == 2 and digits.isdigit():
                predictions.append(digits)

                # Early exit: first two valid results are the same
                if len(predictions) >= 2 and predictions[-1] == predictions[-2]:
                    print("[提早結束] 前兩張結果相同，直接採用")
                    break
            else:
                print("    無效，繼續")
        except Exception as e:
            print(f"  第{i}張 OCR 錯誤: {e}")

        # Shorter delay between captures
        if i < 3:
            time.sleep(0.06)

    if not predictions:
        print("[OCR 失敗] 沒有讀到有效兩位數")
        return None

    # If we broke early with two matching, just use it; otherwise vote
    if len(predictions) >= 2 and predictions[0] == predictions[1]:
        best = predictions[0]
        print(f"[採用] {best}（前兩張一致）")
        return best

    vote = Counter(predictions)
    best_digits, count = vote.most_common(1)[0]
    print(f"[投票結果] {dict(vote)} → 採用 {best_digits} ({count}/{len(predictions)} 票)")
    return best_digits


def click_at(pos, delay=0.3):
    if pos:
        pyautogui.click(pos[0], pos[1])
        print(f"[點擊] ({pos[0]}, {pos[1]})")
        time.sleep(delay)
        return True
    return False


def handle_captcha(MAX_RETRIES):       

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- 第 {attempt} 次嘗試 ---")

        window_tl = find_template_topleft("templates/captcha_window.png", threshold=0.65)
        if not window_tl:
            print("沒有偵測到驗證碼視窗")
            return False

        target_digits = ocr_from_relative_area(window_tl)

        if not target_digits:
            print("[OCR 失敗] 沒有讀到有效兩位數，改為按下 0 和 0")
            target_digits = "00"
            # 不直接重試或結束，改為強制點擊 00 繼續流程

        #if not target_digits:
        #    time.sleep(0.6)
        #    continue

        print(f"[目標數字] {target_digits}")
        print("="*25) 

        success = True
        for d in target_digits:
            if d not in DIGIT_TEMPLATES:
                print(f"[錯誤] 缺少數字 {d} 的按鈕模板")
                success = False
                break
            btn_pos = find_template_center(DIGIT_TEMPLATES[d], threshold=0.655)
            if not btn_pos or not click_at(btn_pos, delay=0.25):
                print(f"[錯誤] 無法點擊數字 {d}")
                success = False
                break

        if not success:
            time.sleep(0.6)
            continue

        print("點擊完成，等待反應...")
        print("="*25)
        time.sleep(1.2)  # reduced from 1.8

        if find_template_topleft("templates/error_prompt.png", threshold=0.65):
            print("[結果] 出現錯誤提示")
            confirm = find_template_center("templates/btn_confirm.png", threshold=0.65)
            if confirm:
                click_at(confirm, delay=0.3)
            else:
                print("[警告] 找不到 btn_confirm.png")
            time.sleep(0.8)
            continue

        if not find_template_topleft("templates/captcha_window.png", threshold=0.65):
            print("[成功] 驗證碼視窗已消失")
            return True
        else:
            print("[未知狀態] 視窗仍在，稍後重試")
            time.sleep(0.6)

    print("[失敗] 達到最大重試次數")
    return False


if __name__ == "__main__":
    try:
        print("" + "="*25)
        print("偵測驗證碼視窗")
        print("="*25)
        handle_captcha()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")