import pyautogui
import cv2
import numpy as np
import time
import os

# ==================== 設定區 ====================
# 匹配信心度（0.0~1.0），越高越嚴格，建議從 0.75 開始調
CONFIDENCE = 0.78

# 模板圖片路徑
TEMPLATE_PATH = "templates/magic_book.png"      # ------- Change your picture here ------- #
SEARCH_REGION = (610, 580, 270, 170)            # None or（left, top, width, height）

# 等待室確認模板
READY_TEMPLATE_PATH = "templates/ready.png"
READY_SEARCH_REGION = (1000, 770, 290, 180)

# 點擊後等待時間（秒），讓畫面有時間切換到等待室
WAIT_AFTER_CLICK = 2

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

def click_magic_book():
    """
    尋找並點擊「魔書解密」縮圖
    成功回傳 True
    """
    found, pos, score = find_template(TEMPLATE_PATH, confidence=CONFIDENCE, region=SEARCH_REGION)

    if found:
        print(f"[成功] 找到魔書解密入口！信心度：{score:.3f}，點擊位置：{pos}")
        pyautogui.click(pos[0], pos[1])
        return True
    else:
        print(f"[未找到] 最高信心度：{score:.3f}（需要 ≥ {CONFIDENCE}）")
        return False


def is_ready_in_waiting_room():
    """
    檢查等待室是否已出現 ready.png
    成功回傳 True
    """
    found, pos, score = find_template(
        READY_TEMPLATE_PATH,
        confidence=CONFIDENCE,
        region=READY_SEARCH_REGION,
    )
    if found:
        print(f"[確認] 找到 ready.png！信心度：{score:.3f}，位置：{pos}")
        return True
    print(f"[未確認] ready.png 最高信心度：{score:.3f}（需要 ≥ {CONFIDENCE}）")
    return False


def enter_waiting_room():
    """
    持續點擊魔書，直到確認 ready.png 出現在等待室
    """
    attempts = 0
    while True:
        attempts += 1
        print(f"\n--- click_map 第 {attempts} 次嘗試 ---")

        if click_magic_book():
            print(f"已點擊！等待 {WAIT_AFTER_CLICK} 秒讓畫面切換...")
            time.sleep(WAIT_AFTER_CLICK)
            if is_ready_in_waiting_room():
                print("已確認進入等待室。")
                return True
            print("尚未確認進入等待室，準備重新點擊魔書...")
        else:
            print("1 秒後重試...")
            time.sleep(1)


# ==================== 主程式（測試用） ====================
def main():
    
    """ # 給你 3 秒時間切換到遊戲視窗
    print("\n3 秒後開始搜尋...")
    for i in range(3, 0, -1):
        print(f"{i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n開始！\n") """

    
    print("=" * 25)
    print(f"開始搜尋[{TEMPLATE_PATH}]")
    print("=" * 25)

    enter_waiting_room()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
