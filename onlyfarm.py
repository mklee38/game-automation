import time
import subprocess
import sys
import os
import pyautogui
import pygetwindow as gw
import interception


import popups
import farm   # 你的 farm.py

import random

# ===== 每 20 分鐘使用一次 Buff =====
import time
from use_buff import use_buff   # 請依你的檔案路徑調整

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05



def handle_popups_once():
    """執行 popups 邏輯。"""
    print("\n" + "=" * 40)
    print(f"{' '*10}<!偵測彈出訊息!>")
    print("=" * 40)
    popups.handle_popups(popups.PATH_1, 
                         popups.PATH_2, 
                         popups.PATH_3, 
                         popups.PATH_4,
                         popups.PATH_5,
                         popups.PATH_6)


def main():

    # ===== 每 24 分鐘去一次農場 =====
    FARM_INTERVAL = 24 * 60          # 24 分鐘（秒）
    last_farm_time = time.time()     # 從現在開始計時 → 第一次不會立刻去農場

    print("#" * 40)
    print("啟動: 自動化系統 (按 Ctrl+C 可隨時中斷)")
    print("#" * 40)

    # ===== 只在程式最開始初始化 interception 一次 =====
    print("初始化 interception...")
    interception.auto_capture_devices()
    print("interception 初始化完成")
    # popup_proc = start_popups_separate_console()

   
    # ===== 程式一開始先去一次農場種植 =====
    print("\n" + "#" * 40)
    print("程式啟動：先前往農場種植作物")
    print("#" * 40)
    farm.main()
    last_farm_time = time.time()     # 計時從第一次農場完成後開始
    print("[Farm] 初次農場完成，24 分鐘計時開始")

    cycle = 0

    try:
        while True:
            cycle += 1
            print(f"\n\n[開始第 {cycle} 輪循環]")
        
            # ===== 每 24 分鐘執行一次農場 =====
            now = time.time()
            elapsed = now - last_farm_time
            remaining = int(FARM_INTERVAL - elapsed)

            if remaining <= 0:
                print(f"\n[Farm] 已超過 {FARM_INTERVAL//60} 分鐘，開始執行農場腳本...")
                farm.main()
                last_farm_time = time.time()          # 計時從「農場完成」後重新開始
                print("[Farm] 農場完成，24 分鐘計時重新開始")
            else:
                # 等待期間持續顯示剩餘時間（每秒更新同一行）
                print("[Farm] 開始等待下次農場...")
                while True:
                    now = time.time()
                    elapsed = now - last_farm_time
                    remaining = int(FARM_INTERVAL - elapsed)
                    if remaining <= 0:
                        break
                    mins = remaining // 60
                    secs = remaining % 60
                    # 用 \r 覆蓋同一行，持續顯示倒數
                    print(f"\r[Farm] 距離下次農場還有 {mins:02d} 分 {secs:02d} 秒，繼續等待...   ", end="", flush=True)
                    time.sleep(1)
                print()  # 倒數結束後換行
                print(f"[Farm] 等待結束，開始執行農場腳本...")

                for i in range(0, 2):
                    try:
                        windows = gw.getWindowsWithTitle('Tales Runner')
                        if windows:
                            window = windows[0]
                            if window.isMinimized:
                                window.restore()
                            window.activate()
                            time.sleep(0.5)
                    except Exception:
                        pass

                farm.main()
                last_farm_time = time.time()
                print("[Farm] 農場完成，24 分鐘計時重新開始")

    except KeyboardInterrupt:
        print("\n\n[使用者中斷] 正在停止...")
    except Exception as e:
        print(f"\n[主循環錯誤] {e}")
    # finally:
    #     if popup_proc is not None and popup_proc.poll() is None:
    #         print("[Popup] 正在關閉獨立的 popups 視窗...")
    #         popup_proc.terminate()
    #         try:
    #             popup_proc.wait(timeout=3)
    #         except subprocess.TimeoutExpired:
    #             popup_proc.kill()
    #     print("主循環已結束。")


if __name__ == "__main__":
    main()
