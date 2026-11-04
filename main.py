"""
Tales Runner 自動化主循環
整合 click_map / captcha / start / script / lobby，並同時執行 popups。

循環流程：
1. click_map：持續點擊魔書直到成功進入地圖
2. captcha：立刻檢查驗證碼（沒有就提早結束）
3. start：持續等待 start.png 出現（代表比賽開始）→ 再等 8 秒讓角色落地
4. script：執行 80 秒控制腳本
5. lobby：持續等待 lobby.png 出現（代表回到大廳）
6. 回到步驟 1

popups.py 會在獨立的終端機視窗中同時執行，訊息不會混在一起。
按 Ctrl+C 可隨時安全中斷主循環。
"""

import time
import subprocess
import sys
import os
import pyautogui

import click_map
import captcha
import start
import script_no_jump
import lobby

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def start_popups_separate_console():
    """在新的終端機視窗啟動 popups.py。"""
    popups_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "popups.py")
    if not os.path.exists(popups_path):
        print(f"[警告] 找不到 popups.py：{popups_path}")
        return None

    creationflags = 0
    if os.name == "nt":
        # Windows：開新的 console 視窗
        creationflags = subprocess.CREATE_NEW_CONSOLE

    proc = subprocess.Popen(
        [sys.executable, popups_path],
        creationflags=creationflags,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    print(f"[Popup] 已在獨立視窗啟動 popups.py（PID={proc.pid}）")
    return proc


def enter_map():
    """執行 click_map 邏輯：持續點擊魔書，直到確認 ready.png 出現。"""
    print("\n" + "=" * 40)
    print("步驟 1：點擊魔書進入地圖（確認 ready.png）")
    print("=" * 40)
    click_map.enter_waiting_room()


def handle_captcha_once():
    """執行 captcha 邏輯（沒有驗證碼時會提早結束）。"""
    print("\n" + "=" * 40)
    print("步驟 2：檢查驗證碼")
    print("=" * 40)
    captcha.handle_captcha()


def wait_for_start():
    """執行 start 邏輯：直到偵測到 start.png，再等待 8 秒。"""
    print("\n" + "=" * 40)
    print("步驟 3：等待比賽開始 (start.png)")
    print("=" * 40)
    attempts = 0
    while True:
        attempts += 1
        print(f"--- start 第 {attempts} 次嘗試 ---")
        found = start.find_template(
            start.TEMPLATE_PATH,
            confidence=start.CONFIDENCE,
            region=None,
            grayscale=False,
        )
        if found:
            print("偵測到 start.png，比賽開始！")
            print("等待 8 秒確保角色落地...")
            time.sleep(8)
            return
        print("1 秒後重試...")
        time.sleep(1)


def run_race_script():
    """執行 script.py 的 80 秒控制。"""
    print("\n" + "=" * 40)
    print("步驟 4：執行比賽控制腳本")
    print("=" * 40)
    script_no_jump.main()


def wait_for_lobby():
    """執行 lobby 邏輯：直到偵測到 lobby.png。"""
    print("\n" + "=" * 40)
    print("步驟 5：等待回到大廳 (lobby.png)")
    print("=" * 40)
    attempts = 0
    while True:
        attempts += 1
        print(f"--- lobby 第 {attempts} 次嘗試 ---")
        found = lobby.find_template(
            lobby.TEMPLATE_PATH,
            confidence=lobby.CONFIDENCE,
            region=None,
            grayscale=False,
        )
        if found:
            print("偵測到 lobby.png，已回到大廳。")
            return
        print("1 秒後重試...")
        time.sleep(1)


def main():
    print("=" * 50)
    print("Tales Runner 自動化主循環啟動")
    print("按 Ctrl+C 可隨時中斷")
    print("=" * 50)

    popup_proc = start_popups_separate_console()

    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n{'#' * 50}")
            print(f"開始第 {cycle} 輪循環")
            print(f"{'#' * 50}")

            enter_map()
            handle_captcha_once()
            wait_for_start()
            run_race_script()
            wait_for_lobby()

            print(f"\n第 {cycle} 輪完成，準備下一輪...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[使用者中斷] 正在停止...")
    except Exception as e:
        print(f"\n[主循環錯誤] {e}")
    finally:
        if popup_proc is not None and popup_proc.poll() is None:
            print("[Popup] 正在關閉獨立的 popups 視窗...")
            popup_proc.terminate()
            try:
                popup_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                popup_proc.kill()
        print("主循環已結束。")


if __name__ == "__main__":
    main()
