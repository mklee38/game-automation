"""
Tales Runner 自動化主循環
整合 click_map / captcha / start / script / lobby，並同時執行 popups。

循環流程：
1. click_map：持續點擊魔書直到成功進入地圖（確認 ready.png）
2. captcha：立刻檢查驗證碼（沒有就提早結束）
3. start：持續等待 start_MCJ.png 出現（代表比賽開始）→ 再等 8 秒讓角色落地
4. script：執行 80 秒控制腳本（含背景隨機跳躍）
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
import interception

import action_MCJ
import click_map
import captcha
import start_MCJ
import script
import lobby
import popups

import click_my_room
import click_return

import farm   # 你的 farm.py

import random

# ===== 每 20 分鐘使用一次 Buff =====
import time
from use_buff import use_buff   # 請依你的檔案路徑調整

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


# def start_popups_separate_console():
#     """在新的終端機視窗啟動 popups.py。"""
#     popups_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "popups.py")
#     if not os.path.exists(popups_path):
#         print(f"[警告] 找不到 popups.py：{popups_path}")
#         return None

#     creationflags = 0
#     if os.name == "nt":
#         # Windows：開新的 console 視窗
#         creationflags = subprocess.CREATE_NEW_CONSOLE

#     proc = subprocess.Popen(
#         [sys.executable, popups_path],
#         creationflags=creationflags,
#         cwd=os.path.dirname(os.path.abspath(__file__)),
#     )
#     print(f"[Popup] 已在獨立視窗啟動 popups.py（PID={proc.pid}）")
#     return proc


def enter_map():
    """執行 click_map 邏輯：持續點擊地圖，直到indicator出現。"""
    print("\n" + "=" * 40)
    print("步驟 1：點擊圖標進入")
    print("=" * 40)
    click_map.enter_waiting_room()

def enter_my_room():
    print("\n" + "=" * 40)
    print("[點擊圖標進入]")
    print("=" * 40)
    click_my_room.enter_room()

def return_homepage():
    print("\n" + "=" * 40)
    print("[點擊圖標進入]")
    print("=" * 40)
    click_return.enter_room()

def handle_captcha_once():
    """執行 captcha 邏輯（沒有驗證碼時會提早結束）。"""
    print("\n" + "=" * 40)
    print("步驟 2：檢查驗證碼")
    print("=" * 40)
    captcha.handle_captcha(captcha.MAX_RETRIES)


def wait_for_start():
    """執行 start 邏輯：直到偵測到 start，或逾時後重新進入等待室。"""
    print("\n" + "=" * 40)
    print("步驟 3：等待比賽開始")
    print("=" * 40)

    while True:
        success = start_MCJ.wait_for_start_with_timeout()
        if success:
            print("比賽即將開始！")
            # print("等待 8 秒確保角色落地...")
            # time.sleep(8)
            return
        else:
            print("逾時未偵測到開始指示，重新執行 click_map 進入等待室...")
            enter_map()
            handle_captcha_once()
            handle_popups_once()




def run_race_script():
    
    print("\n" + "=" * 40)
    print("步驟 4：執行比賽控制腳本（含隨機跳躍）")
    print("=" * 40)
    action_MCJ.main()
     
    
    # script.main()


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
        print("5 秒後重試...")
        time.sleep(5)

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

    # ===== 每 20 分鐘使用一次 Buff =====
    BUFF_INTERVAL = 20 * 60          # 20 分鐘（秒）
    last_buff_time = 0               # 設成 0 讓程式一開始就先用一次 buff

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
            
            # Whole script logic start
            handle_popups_once()            
            enter_map()                     # step 1                    
            handle_captcha_once()           # step 2
            handle_popups_once()              
            wait_for_start()                # step 3
            run_race_script()               # step 4
            wait_for_lobby()                # step 5


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
                mins = remaining // 60
                secs = remaining % 60
                print(f"[Farm] 距離下次農場還有 {mins:02d} 分 {secs:02d} 秒，繼續下一局遊戲")


            

            """ # ===== 每 20 分鐘使用一次 Buff ===== (唔想用就comment咗佢)
            handle_popups_once()
            enter_my_room()             
            handle_popups_once()
            
            now = time.time()
            if now - last_buff_time >= BUFF_INTERVAL:
                print(f"[Buff] 已超過 {BUFF_INTERVAL//60} 分鐘，開始使用 Buff...")
                success = use_buff()
                if not success:
                    print("[Buff] 使用失敗，程式結束")
                    break
                last_buff_time = time.time()
                print("[Buff] 使用完成，計時重新開始")

            handle_popups_once()
            return_homepage()
            time.sleep(1)  """


            # Go to myHome after each game
            # time.sleep(random.uniform(2, 5))   # add some delay
            
            # handle_popups_once()
            # enter_my_room()
            # time.sleep(random.uniform(3, 5))   # add some delay

            # handle_popups_once()
            # return_homepage()
            # time.sleep(random.uniform(3, 5))   # add some delay

            # print(f"\n第 {cycle} 輪完成，準備下一輪...")
            # time.sleep(1)

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
