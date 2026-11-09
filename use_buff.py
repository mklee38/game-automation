import time
import os
import sys
import pyautogui
import cv2
import numpy as np
import interception

# 初始化 interception（只需呼叫一次）
interception.auto_capture_devices()

CONFIDENCE = 0.75
TEMPLATES_DIR = "templates"

def find_template_center(template_name, confidence=CONFIDENCE, region=None):
    """
    找模板並回傳中心座標
    回傳: (found, center_pos, score, topleft_pos)
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.exists(template_path):
        print(f"[錯誤] 找不到模板：{template_path}")
        return False, None, 0.0, None

    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path)
    if template is None:
        print(f"[錯誤] 無法讀取模板：{template_path}")
        return False, None, 0.0, None

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape[:2]
        offset_x = region[0] if region else 0
        offset_y = region[1] if region else 0

        topleft_x = max_loc[0] + offset_x
        topleft_y = max_loc[1] + offset_y
        center_x = topleft_x + w // 2
        center_y = topleft_y + h // 2

        print(f"[成功] 找到 {template_name}！信心度：{max_val:.3f}，中心：{(center_x, center_y)}")
        return True, (center_x, center_y), max_val, (topleft_x, topleft_y)
    else:
        return False, None, max_val, None


def click_at(pos):
    """使用 interception 點擊指定座標（中心點）"""
    if pos:
        x, y = pos
        interception.click(x, y)
        print(f"[點擊] 位置：{pos}")
        time.sleep(0.3)


def use_buff():
    """
    在房間使用 buff 道具
    假設目前已在房間內
    任一失敗即結束並回傳 False
    """
    print("\n=== 開始使用 Buff ===")

    # 1. 找 other.png 並點擊中心
    print("步驟 1：尋找 other.png")
    found, pos, score, _ = find_template_center(
        "other.png",
        region=(940, 100, 80, 70)
    )
    if not found:
        print(f"[失敗] 找不到 other.png（最高分數：{score:.3f}）")
        return False
    click_at(pos)
    time.sleep(0.5)

    # 2. 找 buff.png 並點擊中心（同時保留左上角供相對定位使用）
    print("步驟 2：尋找 buff.png")
    found, buff_center, score, buff_topleft = find_template_center(
        "buff.png",
        region=(560, 150, 1250, 830)
    )
    if not found:
        print(f"[失敗] 找不到 buff.png（最高分數：{score:.3f}）")
        return False
    click_at(buff_center)
    time.sleep(0.5)

    # 3. 以 buff.png 左上角為 (0,0) 計算 use.png 搜尋區域
    print("步驟 3：尋找 use.png（相對 buff.png）")
    use_region = (
        buff_topleft[0] + 9,
        buff_topleft[1] + 93,
        51,
        118
    )
    print(f"use.png 搜尋區域：{use_region}")
    found, use_pos, score, _ = find_template_center(
        "use.png",
        region=use_region
    )
    if not found:
        print(f"[失敗] 找不到 use.png（最高分數：{score:.3f}）")
        return False
    click_at(use_pos)

    # 4. 等待 1 秒 → 找 btn_yes.png 並點擊中心
    print("步驟 4：等待 1 秒後尋找 btn_yes.png")
    time.sleep(0.5)
    found, use_pos, score, _ = find_template_center("btn_yes.png")
    if not found:
        print(f"[失敗] 第一次找不到 btn_yes.png（最高分數：{score:.3f}）")
        return False
    click_at(use_pos)

    print(f"[移動滑鼠] 移到空白處 (860, 20) 避免游標擋住按鈕")
    pyautogui.moveTo(860, 20)
    time.sleep(0.15)

    # 5. 再等待 1 秒 → 再找一次 btn_yes.png 並點擊中心
    print("步驟 5：再等待 1 秒後尋找 btn_confirm.png")
    # time.sleep(0.5)
    found, confirm_pos, score, _ = find_template_center("btn_confirm.png")
    if not found:
        print(f"[失敗] 找不到 btn_confirm.png（最高分數：{score:.3f}）")
        return False
    click_at(confirm_pos)

    print("=== Buff 使用完成 ===\n")
    return True


# 測試用：失敗時直接結束程式
if __name__ == "__main__":
    success = use_buff()
    if not success:
        print("使用 Buff 失敗，程式結束")
        sys.exit(1)