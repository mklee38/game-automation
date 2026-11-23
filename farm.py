"""
Tales Runner - Farm Automation (with retry)
"""

import pyautogui
import cv2
import numpy as np
import time
import os

import popups

# ==================== 設定區 ====================
CONFIDENCE = 0.78

# 重試設定
MAX_RETRIES = 15          # 最多重試次數（約 15 秒）
RETRY_INTERVAL = 1.0      # 每次重試間隔（秒）

WAIT_SHORT = 1.0
WAIT_LOAD = 4.0
WAIT_AFTER_COLLECT = 2.0

# 模板路徑
PATH_GOTO_FARM      = "templates/farm/goto_farm.png"
PATH_GOTO_MY_FARM   = "templates/farm/goto_my_farm.png"
PATH_CROPS_MGMT     = "templates/farm/crops_management.png"
PATH_COLLECT_ALL    = "templates/farm/collect_all.png"
PATH_BIG_CLOSE      = "templates/farm/big_close.png"
PATH_FARM_STORE     = "templates/farm/farm_store.png"
PATH_FIELD_CAT      = "templates/farm/field_category.png"
PATH_STRAWBERRY     = "templates/farm/strawberry_field.png"
PATH_FARM_GRIDS     = "templates/farm/farm_grids.png"
PATH_BUY_ALL        = "templates/farm/buy_all.png"
PATH_BUY            = "templates/farm/buy.png"
PATH_SMALL_CLOSE    = "templates/farm/small_close.png"
PATH_HOMEPAGE       = "templates/farm/homepage.png"

PATH_BTN_YES        = "templates/popups/btn_yes.png"
PATH_BTN_CONFIRM    = "templates/popups/btn_confirm.png"

# ==================== 核心函數 ====================
def find_template(template_path, confidence=CONFIDENCE, region=None):
    if not os.path.exists(template_path):
        print(f"[錯誤] 找不到模板檔案：{template_path}")
        return False, None, 0.0

    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path)
    if template is None:
        print(f"[錯誤] 無法讀取模板：{template_path}")
        return False, None, 0.0

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        if region:
            center_x += region[0]
            center_y += region[1]
        return True, (center_x, center_y), max_val
    else:
        return False, None, max_val


def click_until_found(template_path, label="", max_retries=MAX_RETRIES, 
                      interval=RETRY_INTERVAL, confidence=CONFIDENCE, 
                      region=None, wait_after=0.6):
    """
    持續尋找模板直到找到並點擊，或超過最大重試次數。
    每次都會印出信心度。
    回傳 True（成功）或 False（失敗）
    """
    name = label or os.path.basename(template_path)
    print(f"\n[尋找] {name}")

    for attempt in range(1, max_retries + 1):
        found, pos, score = find_template(template_path, confidence=confidence, region=region)

        if found:
            print(f"  [找到] 第 {attempt} 次 | 信心度：{score:.3f} | 位置：{pos}")
            pyautogui.click(pos[0], pos[1])
            time.sleep(wait_after)
            return True
        else:
            print(f"  [未找到] 第 {attempt}/{max_retries} 次 | 信心度：{score:.3f}（需要 ≥ {confidence}）")
            if attempt < max_retries:
                time.sleep(interval)

    print(f"  [失敗] 超過最大重試次數，放棄 {name}")
    return False

def click_grid_with_delay(template_path, label="放置格子", max_retries=MAX_RETRIES):
    print(f"\n[尋找] {label}")
    for attempt in range(1, max_retries + 1):
        found, pos, score = find_template(template_path, confidence=CONFIDENCE)
        if found:
            print(f"  [找到] 第 {attempt} 次 | 信心度：{score:.3f} | 位置：{pos}")
            pyautogui.moveTo(pos[0], pos[1], duration=0.25)
            print("  → 已移動滑鼠，等待 0.1 秒...")
            time.sleep(0.1)  # delay to success to grow crops
            pyautogui.click()
            return True
        else:
            print(f"  [未找到] 第 {attempt}/{max_retries} 次 | 信心度：{score:.3f}")
            time.sleep(RETRY_INTERVAL)
    return False


def click_popup_until_found(template_path, label, max_retries=8):
    """專門給彈窗按鈕用（是 / 確認）"""
    return click_until_found(template_path, label=label, max_retries=max_retries, interval=0.7)


def handle_all_popups():
    print("--- 處理彈窗 ---")
    popups.handle_popups(
        popups.PATH_1, popups.PATH_2, popups.PATH_3,
        popups.PATH_4, popups.PATH_5, popups.PATH_6
    )


# ==================== 主流程 ====================
def main():
    handle_all_popups()
    print("=" * 55)
    print("開始農場自動化腳本（含重試）")
    print("=" * 55)

    # ---------- Step 1 ----------
    print("\n[Step 1] 從大廳進入農場")
    if not click_until_found(PATH_GOTO_FARM, "進入農場"):
        print("無法進入農場，腳本結束。")
        return
    click_popup_until_found(PATH_BTN_YES, "確認進入 (btn_yes)")
    handle_all_popups()

    # ---------- Step 2 ----------
    print("\n[Step 2] 進入我的農田")
    click_until_found(PATH_GOTO_MY_FARM, "進入我的農田")
    print(f"等待農田載入 {WAIT_LOAD} 秒...")
    time.sleep(WAIT_LOAD)
    handle_all_popups()

    # ---------- Step 3~5：收成（可選）----------
    print("\n[Step 3-5] 檢查是否有作物可收成")
    if click_until_found(PATH_CROPS_MGMT, "作物管理", max_retries=1):  # 只試 5 次，沒有就跳過
        print("開始收成兩輪...")
        for r in range(1, 3):
            print(f"  第 {r} 輪收成")
            click_until_found(PATH_COLLECT_ALL, "全部收成")
            time.sleep(WAIT_AFTER_COLLECT)
            click_popup_until_found(PATH_BTN_CONFIRM, "確認收成")
        click_until_found(PATH_BIG_CLOSE, "關閉作物管理")
    else:
        print("沒有作物管理介面，跳過收成。")
    handle_all_popups()

    # ---------- Step 6~12：購買並種植 ----------
    print("\n[Step 6-12] 購買並種植草莓田")
    click_until_found(PATH_FARM_STORE, "打開農場商店")
    click_until_found(PATH_FIELD_CAT, "田地分類")

    print("開始種植 25 塊草莓田...")
    for i in range(1, 26):
        print(f"\n--- 種植第 {i}/25 塊 ---")
        click_until_found(PATH_STRAWBERRY, "草莓田")
        click_grid_with_delay(PATH_FARM_GRIDS)

    click_until_found(PATH_BUY_ALL, "全部購買")
    click_until_found(PATH_BUY, "購買")
    click_popup_until_found(PATH_BTN_YES, "確認1")
    click_popup_until_found(PATH_BTN_YES, "確認2")
    click_popup_until_found(PATH_BTN_CONFIRM, "最終確認")
    click_until_found(PATH_SMALL_CLOSE, "關閉商店")
    handle_all_popups()

    # ---------- Step 13~14 ----------
    print("\n[Step 13-14] 返回大廳")
    click_until_found(PATH_HOMEPAGE, "回到首頁")
    click_popup_until_found(PATH_BTN_YES, "確認離開")

    print("\n" + "=" * 55)
    print("農場自動化完成！")
    print("=" * 55)


if __name__ == "__main__":
    try:
        pyautogui.FAILSAFE = True
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
        import traceback
        traceback.print_exc()