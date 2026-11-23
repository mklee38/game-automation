import pyautogui
import cv2
import numpy as np
import time
import os

# ==================== 設定區 ====================
CONFIDENCE = 0.78

# 模板圖片路徑
TEMPLATE_PATH_1 = "templates/game_start/MCJ_start.png"         
SEARCH_REGION_1 = (0, 150, 60, 40)           # None 

TEMPLATE_PATH_2 = "templates/game_start/MCJ_start_extra.png"      
SEARCH_REGION_2 = (660, 100, 190, 280)              # None

# 等待開始的最長時間（秒）
START_TIMEOUT = 90


# ==================== 核心函數 ====================
def find_template(TEMPLATE_PATH, confidence=CONFIDENCE, region=None, grayscale=False):    
   
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[錯誤] 找不到模板檔案：{TEMPLATE_PATH}")
        return False, None, 0.0

    # 截圖
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 讀取模板
    template = cv2.imread(TEMPLATE_PATH)
    if template is None:
        print(f"[錯誤] 無法讀取模板：{TEMPLATE_PATH}")
        return False, None, 0.0

    # 可選：轉灰階
    if grayscale:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape[:2]
        
        local_center_x = max_loc[0] + w // 2
        local_center_y = max_loc[1] + h // 2

        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0

        center_x = local_center_x + offset_x
        center_y = local_center_y + offset_y

        print(f"[成功] 找到了{TEMPLATE_PATH}！信心度：{max_val:.3f}，所在位置：{(center_x, center_y)}")
        pyautogui.moveTo(center_x, center_y)
        return True
    else:
        print(f"[未找到] 最高信心度：{max_val:.3f}（需要 ≥ {CONFIDENCE}）")
        return False


def wait_for_start_with_timeout(timeout=START_TIMEOUT):
    """
    等待 start 指示出現，最多等待 timeout 秒。
    成功偵測到回傳 True，逾時回傳 False。
    """
    print(f"開始等待比賽開始（最多 {timeout} 秒）...")
    start_time = time.time()
    attempts = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            print(f"[逾時] 已等待 {timeout} 秒仍未偵測到開始指示，將重新進入等待室")
            return False

        attempts += 1
        print(f"--- start 第 {attempts} 次嘗試（已等待 {elapsed:.1f} 秒）---")

        found = find_template(
            TEMPLATE_PATH_1,
            confidence=CONFIDENCE,
            region=SEARCH_REGION_1,
            grayscale=False,
        ) or find_template(
            TEMPLATE_PATH_2,
            confidence=CONFIDENCE,
            region=SEARCH_REGION_2,
            grayscale=False,
        )

        if found:
            print("比賽即將開始！")
            return True

        time.sleep(1)


# ==================== 主程式（測試用） ====================
def main():
    print("=" * 25)
    print(f"開始搜尋[{TEMPLATE_PATH_1} and {TEMPLATE_PATH_2}]")
    print("=" * 25)
    print()

    success = wait_for_start_with_timeout()
    if success:
        print("成功偵測到開始")
    else:
        print("逾時，需要重新進入地圖")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
