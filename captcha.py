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
# 根據使用者提供：2_digits.png 相對 captcha_window.png 左上 (158, 28)，右下 (245, 88)
TARGET_OFFSET_X = 158
TARGET_OFFSET_Y = 28
TARGET_WIDTH    = 87   # 245 - 158
TARGET_HEIGHT   = 60   # 88 - 28
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
    denoised = cv2.fastNlMeansDenoising(v_channel, None, h=6)     # origin h = 12
    return denoised


def ocr_single_half(half_bgr, reader, label, i):
    """對單一半邊影像做 OCR，期望得到單一數字。同時輸出 debug 圖片。"""
    
    debug_dir = "debug_captcha"                        # 設定 debug 圖片輸出資料夾（會自動建立）
    os.makedirs(debug_dir, exist_ok=True)

    # 儲存原始半邊圖（方便除錯）
    cv2.imwrite(os.path.join(debug_dir, f"debug_{label}_raw_{i}.png"), half_bgr)

    denoised = preprocess_blue_noise_captcha(half_bgr)
    # 儲存去噪後的半邊圖
    cv2.imwrite(os.path.join(debug_dir, f"debug_{label}_denoised_{i}.png"), denoised)

    try:
        results = reader.readtext(denoised, detail=1, allowlist='0123456789', mag_ratio=1.5)
        if not results:
            print(f"    {label} 第{i}張: 無辨識結果")
            return None

        # 取信心最高的結果
        best = max(results, key=lambda r: r[2])
        text = best[1].strip()
        conf = best[2]
        print(f"    {label} 第{i}張: '{text}' (信心={conf:.2f})")

        if len(text) == 1 and text.isdigit():
            return text
        else:
            print(f"    {label} 結果長度不為 1 或非數字")
            return None
    except Exception as e:
        print(f"    {label} 第{i}張 OCR 錯誤: {e}")
        return None


def ocr_from_relative_area(window_topleft):
    print("正在載入 EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=False, quantize=True)
    print("EasyOCR 載入完成\n")

    left = window_topleft[0] + TARGET_OFFSET_X
    top  = window_topleft[1] + TARGET_OFFSET_Y

    print(f"[裁切] 目標區域：({left}, {top}, {TARGET_WIDTH}x{TARGET_HEIGHT})")
    print("[OCR] 最多擷取 5 張（前兩張相同即提早結束）")
    print("[方法] 將兩位數區域平均切成左右兩半，分別辨識後再組合")

    predictions = []

    MAX_CAPTURES = 5          # ← capture number   (3)
    CAPTURE_INTERVAL = 0.03   # ← capture interval in seconds   (0.06)

    for i in range(1, MAX_CAPTURES + 1):       # 自訂擷取數目
        crop = pyautogui.screenshot(region=(left, top, TARGET_WIDTH, TARGET_HEIGHT))
        crop_cv = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2BGR)

        # 可選：儲存完整裁切圖
        # cv2.imwrite(f"debug_full_raw_{i}.png", crop_cv)

        # 平均切分左右
        mid = crop_cv.shape[1] // 2
        left_half = crop_cv[:, :mid]
        right_half = crop_cv[:, mid:]

        left_digit = ocr_single_half(left_half, reader, "left", i)
        right_digit = ocr_single_half(right_half, reader, "right", i)

        if left_digit and right_digit:
            digits = left_digit + right_digit
            predictions.append(digits)
            print(f"  第{i}張組合結果: '{digits}'")

            # Early exit: first two valid results are the same
            if len(predictions) >= 2 and predictions[-1] == predictions[-2]:
                print("[提早結束] 前兩張結果相同，直接採用")
                break
        else:
            print("    無效（左右任一辨識失敗），繼續")

        # Shorter delay between captures
        if i < MAX_CAPTURES:
            time.sleep(CAPTURE_INTERVAL)

    if not predictions:
        print("[OCR 失敗] 沒有讀到有效兩位數")
        return None

    # If we broke early with two matching, just use it; otherwise vote
    if len(predictions) >= 2 and predictions[0] == predictions[1]:             # break early
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


def handle_captcha(max_retries=None):
    if max_retries is None:
        max_retries = MAX_RETRIES     

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n--- 第 {attempt} 次嘗試 ---")

        window_tl = find_template_topleft("templates/captcha_window.png", threshold=0.78)          # Set threshold
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
        for idx, d in enumerate(target_digits):
            if d not in DIGIT_TEMPLATES:
                print(f"[錯誤] 缺少數字 {d} 的按鈕模板")
                success = False
                break
            btn_pos = find_template_center(DIGIT_TEMPLATES[d], threshold=0.655)        # Set threshold
            if not btn_pos or not click_at(btn_pos, delay=0.25):
                print(f"[錯誤] 無法點擊數字 {d}")
                success = False
                break
            # After clicking the first digit, move mouse away so it doesn't block the second button screenshot
            if idx == 0 and len(target_digits) > 1:
                print(f"[移動滑鼠] 移到空白處 (860, 20) 避免游標擋住按鈕")
                pyautogui.moveTo(860, 20)
                time.sleep(0.15)

        if not success:
            time.sleep(0.6)
            continue

        print("點擊完成，等待反應...")
        print("="*25)
        time.sleep(1.2)  # reduced from 1.8

        if find_template_topleft("templates/error_prompt.png", threshold=0.65):                # Set threshold
            print("[結果] 出現錯誤提示")
            confirm = find_template_center("templates/btn_confirm.png", threshold=0.70)
            if confirm:
                click_at(confirm, delay=1.0)                    # set this delay time
            else:
                print("[警告] 找不到 btn_confirm.png")
            time.sleep(0.8)
            continue

        if not find_template_topleft("templates/captcha_window.png", threshold=0.75):
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
        handle_captcha(MAX_RETRIES)
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
