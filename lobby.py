import pyautogui
import cv2
import numpy as np
import time
import os

# ==================== 設定區 ====================
CONFIDENCE = 0.78

# 模板圖片路徑
TEMPLATE_PATH = "templates/lobby.png"   # ------- Change your picture here ------- #    
SEARCH_REGION = (490, 30, 90, 40)      # None or（left, top, width, height）

# ==================== 核心函數 ====================
def find_template(TEMPLATE_PATH, confidence=CONFIDENCE, region=SEARCH_REGION, grayscale=False):    
    """
    在螢幕上尋找模板圖片
    回傳：(找到與否, 中心座標 (x, y) 或 None, 最高信心度)
    """
    if not os.path.exists(TEMPLATE_PATH):
        print(f"[錯誤] 找不到模板檔案：{TEMPLATE_PATH}")
        return False, None, 0.0

    # 截圖
    screenshot = pyautogui.screenshot(region=region)    # 截取目前螢幕。如果有指定 region，就只截那個範圍。
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)     # 把圖片轉成 NumPy 陣列（OpenCV 需要這種格式）

    # 讀取模板
    template = cv2.imread(TEMPLATE_PATH)     # OpenCV 用來讀取圖檔（如 .png、.jpg 等）的標準函式。
    if template is None:
        print(f"[錯誤] 無法讀取模板：{TEMPLATE_PATH}")
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

        print(f"[成功] 找到了！信心度：{max_val:.3f}，所在位置：{(center_x, center_y)}")
        pyautogui.moveTo(center_x, center_y)
        return True      # True, (center_x, center_y), max_val
    else:
        print(f"[未找到] 最高信心度：{max_val:.3f}（需要 ≥ {CONFIDENCE}）\n")
        return False
# 函數會回傳三個值：
# 第一個：有沒有找到（True / False）
# 第二個：找到的話回傳中心座標 (x, y)，沒找到就回傳 None
# 第三個：這次比對最高的信心度分數


# ==================== 主程式（測試用） ====================
def main():

    """ print("=" * 25)
    # 給你 3 秒時間切換到遊戲視窗
    print("3 秒後開始搜尋...")
    for i in range(3, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n開始！\n") """

    print("=" * 25)
    print(f"開始搜尋[{TEMPLATE_PATH}]")
    print("=" * 25)
    print()

    attempts = 0
    max_attempts = 20  # 最多嘗試次數，避免無限循環

    #while attempts < max_attempts:
    while True:
        attempts += 1
        print(f"--- 第 {attempts} 次嘗試 ---")

        # TODO: 之後在這裡優先檢查驗證碼與彈窗
        # if handle_captcha(): continue
        # if handle_popups(): continue

        if find_template(TEMPLATE_PATH, confidence=CONFIDENCE, region=None, grayscale=False):
            #print("判斷是否正確")
            break
        else:
            print("1 秒後重試...")
            time.sleep(1)

    #if attempts >= max_attempts:
    #    print("\n達到最大嘗試次數，請檢查!!!")
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
