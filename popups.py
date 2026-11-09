"""
Tales Runner 自動化腳本 - 大廳進入「魔書解密」部分
初學者版本，使用 pyautogui + OpenCV 模板匹配

使用前準備：
1. 安裝套件：pip install pyautogui opencv-python numpy
2. 在遊戲大廳截圖，裁切出「魔書解密」縮圖，存成 templates/magic_book.png
3. 遊戲解析度固定為 1024x768，視窗在前景
4. 先手動測試一次，確認點擊位置正確
"""

import pyautogui
import cv2
import numpy as np
import time
import os

# ==================== 設定區 ====================
# 匹配信心度（0.0~1.0），越高越嚴格，建議從 0.75 開始調
CONFIDENCE = 0.78  #0.78     #0.7

# 模板圖片路徑
PATH_1 = "templates/btn_cancel.png"
PATH_2 = "templates/btn_no.png"
PATH_3 = "templates/btn_close.png"
PATH_4 = "templates/btn_confirm.png"
PATH_5 = "templates/btn_allow.png"
PATH_6 = "templates/btn_cross.png"


# 可選：限制搜尋區域（left, top, width, height），加速並減少誤判
SEARCH_REGION = None  # 例如：(100, 200, 800, 400)

# 點擊後等待時間（秒），讓畫面有時間切換到等待室
WAIT_AFTER_CLICK = 1

# ==================== 核心函數 ====================
def find_template(template_path, confidence=CONFIDENCE, region=None, grayscale=False):     #confidence_region = (left, top, width, height)
    """
    在螢幕上尋找模板圖片
    回傳：(找到與否, 中心座標 (x, y) 或 None, 最高信心度)
    """
    if not os.path.exists(template_path):
        print(f"[錯誤] 找不到模板檔案：{template_path}")
        return False, None, 0.0

    # 截圖
    screenshot = pyautogui.screenshot(region=region)    # 截取目前螢幕。如果有指定 region，就只截那個範圍。
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)     # 把圖片轉成 NumPy 陣列（OpenCV 需要這種格式）

    # 讀取模板
    template = cv2.imread(template_path)     # OpenCV 用來讀取圖檔（如 .png、.jpg 等）的標準函式。
    if template is None:
        print(f"[錯誤] 無法讀取模板：{template_path}")
        return False, None, 0.0

    # 可選：轉灰階（有時更穩定）
    if grayscale:
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)      # OpenCV 的模板匹配函數。它會把模板圖片在螢幕截圖上「滑動」比對，計算每個位置的相似度。
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)                  # 從比對結果中找出： (max_val：最高的相似度分數, max_loc：最高分數出現的位置（左上角座標）)

    if max_val >= confidence:
        h, w = template.shape[:2]         #  template.shape，它會回傳一個包含三個數字的元組（Tuple），格式為：(Height, Width, Channels)。• 彩色圖片通常是 3（代表 B、G、R 三個顏色層）；如果是灰階圖片則只有 1。
        center_x = max_loc[0] + w // 2    # max_loc = 「左上角」的座標 , // = Floor Division
        center_y = max_loc[1] + h // 2

        # 如果有指定 region，座標要加上偏移
        if region:
            center_x += region[0]
            center_y += region[1]

        return True, (center_x, center_y), max_val
    else:
        return False, None, max_val
# 函數會回傳三個值：
# 第一個：有沒有找到（True / False）
# 第二個：找到的話回傳中心座標 (x, y)，沒找到就回傳 None
# 第三個：這次比對最高的信心度分數

def click(TEMPLATE_PATH):
   
    found, pos, score = find_template(TEMPLATE_PATH, confidence=CONFIDENCE, region=SEARCH_REGION)

    if found:
        print(f"[找到]信心度：{score:.3f}，點擊位置：{pos}，[{TEMPLATE_PATH}]")
        pyautogui.click(pos[0], pos[1])
        print("已關閉彈出訊息!\n")
        return True
    else:
        print(f"[未找到]信心度：{score:.3f}（需要 ≥ {CONFIDENCE}），[{TEMPLATE_PATH}]")
        return False


def handle_popups(p1, p2, p3, p4, p5, p6):
    if click(p1) or click(p2) or click(p3) or click(p4) or click(p5) or click(p6):
        #time.sleep(WAIT_AFTER_CLICK)
        handle_popups(p1, p2, p3, p4, p5, p6)
    else:
        return False
    

# ==================== 主程式（測試用） ====================
def main():

    print("=" * 25)
    print("偵測通知")
    print("=" * 25)
  
    handle_popups(PATH_1, PATH_2, PATH_3, PATH_4, PATH_5, PATH_6)
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
