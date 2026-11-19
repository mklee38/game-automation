import pyautogui
import cv2
import numpy as np
import os
import time
import interception
import pygetwindow as gw

# 從 version_MCJ 取得版本
from version_MCJ import continuous_detect_until_found

# ==================== 設定區 ====================
CONFIDENCE = 0.75                                      # 動作模板匹配門檻（可依實際調整）
ROUND_START_CONFIDENCE = 0.78

# 回合開始模板
ROUND_START_TEMPLATE = "templates/MCJ/round_start.png"

# 遊戲視窗標題（可依實際視窗名稱調整，支援部分匹配）
GAME_WINDOW_TITLE = "Tales Runner"

# 每個版本的動作模板（放在各自資料夾）
# 結構：templates/MCJ/{version}/{version}_{direction}.png
ACTION_DIRECTIONS = ["left", "right", "up", "down"]

# 方向對應按鍵
DIRECTION_TO_KEY = {
    "left":  "left",
    "right": "right",
    "up":    "up",
    "down":  "down",
}

# 回合設定
TOTAL_ROUNDS = 10
ROUND_DURATION = 4.5                                   # 每回合動作視窗（秒），略大於遊戲的 4 秒
ACTION_POLL_INTERVAL = 0.05                            # 動作偵測輪詢間隔（秒）

# 搜尋區域（可依實際畫面縮小以提升速度）
SEARCH_REGION = (500, 200, 310, 510)  # None


# ==================== 工具函數 ====================
def focus_game_window(title=GAME_WINDOW_TITLE):
    """
    鎖定並啟動遊戲視窗，確保鍵盤輸入能送達。
    回傳 True 表示成功取得焦點。
    """
    try:
        windows = gw.getWindowsWithTitle(title)
        if not windows:
            print(f"[焦點] 找不到標題包含「{title}」的視窗")
            return False

        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.15)  # 給系統一點時間切換焦點
        print(f"[焦點] 已鎖定視窗：{win.title}")
        return True
    except Exception as e:
        print(f"[焦點] 切換視窗失敗：{e}")
        return False


def get_action_templates(version):
    """根據版本回傳 4 個動作模板路徑"""
    base = f"templates/MCJ/{version}"
    return {
        direction: os.path.join(base, f"{version}_{direction}.png")
        for direction in ACTION_DIRECTIONS
    }


def find_best_action(screenshot_bgr, action_templates, confidence=CONFIDENCE):
    """
    在當前畫面找出信心度最高的動作。
    回傳 (direction, score) 或 (None, 0.0)
    """
    best_dir = None
    best_score = 0.0

    for direction, path in action_templates.items():
        if not os.path.exists(path):
            continue

        template = cv2.imread(path)
        if template is None:
            continue

        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_dir = direction

    if best_score >= confidence:
        return best_dir, best_score
    return None, best_score


def detect_round_start(region=SEARCH_REGION, confidence=ROUND_START_CONFIDENCE):
    """偵測回合開始訊息"""
    if not os.path.exists(ROUND_START_TEMPLATE):
        print(f"[錯誤] 找不到回合開始模板：{ROUND_START_TEMPLATE}")
        return False

    screenshot = pyautogui.screenshot(region=region)
    screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    template = cv2.imread(ROUND_START_TEMPLATE)
    if template is None:
        return False

    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val >= confidence


def press_direction(direction):
    """使用 interception 按下對應方向鍵"""
    key = DIRECTION_TO_KEY.get(direction)
    if key:
        interception.press(key)
        print(f"    → 按下 {direction}")


def wait_for_round_start(timeout=7):                                # 自訂time out 時間
    """等待回合開始出現，最多等待 timeout 秒（預設 7 秒）"""
    print(f"等待 round start（最多 {timeout} 秒）...")
    start = time.time()
    while time.time() - start < timeout:
        if detect_round_start():
            print("偵測到 round start！")
            return True
        time.sleep(0.1)
    print(f"等待 round start 逾時（{timeout} 秒），跳過此回合")
    return False



def play_one_round(version, round_num):
    """
    執行單回合：
    1. 等待 round start
    2. 在 ROUND_DURATION 內持續偵測角色動作並按鍵
    規則：同一方向連續出現時只按一次，必須等到不同方向才再按
    """
    print(f"\n===== 第 {round_num}/{TOTAL_ROUNDS} 回合 =====")

    # 每回合開始前重新鎖定遊戲視窗
    focus_game_window()

    if not wait_for_round_start():
        print(f"第 {round_num} 回合未偵測到 round start，跳過")
        return False

    action_templates = get_action_templates(version)
    print(f"使用版本：{version}，開始跟隨動作（{ROUND_DURATION} 秒）")

    last_action = None          # 上一次實際按下的方向
    round_end = time.time() + ROUND_DURATION

    while time.time() < round_end:
        screenshot = pyautogui.screenshot(region=SEARCH_REGION)
        screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        direction, score = find_best_action(screenshot_bgr, action_templates)

        # 只有偵測到「與上次不同」的方向時才按鍵
        # 例如：up, up, up, right → 只會按 up 一次，然後等 right 再按
        if direction and direction != last_action:
            press_direction(direction)
            last_action = direction

        time.sleep(ACTION_POLL_INTERVAL)

    print(f"第 {round_num} 回合結束")
    return True


def main():
    print("=" * 50)
    print("MCJ 動作跟隨腳本")
    print("=" * 50)

    # interception 已在 main_MCJ.py 開頭初始化，這裡不再重複

    # 先鎖定遊戲視窗
    print("\n鎖定遊戲視窗...")
    if not focus_game_window():
        print("警告：無法自動鎖定遊戲視窗，請手動點一下遊戲視窗後繼續")
        time.sleep(3)

    # 1. 先決定版本
    print("\n正在偵測版本...")
    version = continuous_detect_until_found()
    if not version:
        print("無法決定版本，程式結束")
        return

    print(f"\n版本確認：{version}")
    print(f"將使用 templates/MCJ/{version}/ 下的動作模板")

    # 2. 執行 10 回合
    success_count = 0
    for r in range(1, TOTAL_ROUNDS + 1):
        if play_one_round(version, r):
            success_count += 1
        else:
            print(f"第 {r} 回合失敗，繼續下一回合...")

        # 回合之間稍作等待（可依實際調整）
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print(f"全部完成！成功回合：{success_count}/{TOTAL_ROUNDS}")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
        import traceback
        traceback.print_exc()
