import random
import sys
import threading  # 導入多線程庫，處理隨機跳躍
import time
import interception
import pygetwindow as gw

# ==================== 設定區 ====================
KEY_UP = "up"
KEY_DOWN = "down"
KEY_RIGHT = "right"
KEY_LEFT = "left"
KEY_ACCELERATE = "z"
KEY_JUMP = "c"  # (要改按鍵)
KEY_ITEM = "v"  # (要改按鍵)

# 全局控制變數，用於通知背景跳躍線程何時停止
script_running = True


# ==================== 隨機延遲生成器 ====================
# 改為函數形式，確保每次按鍵時都是「當下重新抽籤」，防止被伺服器抓到固定規律
def get_hold_time():
    """快速連續敲擊：70毫秒 至 120毫秒"""
    return random.uniform(0.07, 0.12)


def get_inter_key_interval():
    """「兩次按鍵之間」的間隔時間: 100毫秒 至 250毫秒"""
    return random.uniform(0.1, 0.25)


def get_low_dj_time():
    """低空DJ延遲"""
    return random.uniform(0.25, 0.45)


def get_high_dj_time():
    """高空DJ延遲"""
    return random.uniform(0.05, 0.15)


# ==================== 功能區 ====================
def get_window():
    try:
        windows = gw.getWindowsWithTitle("Tales Runner")
        if windows:
            window = windows[0]
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.5)
    except Exception:
        pass


def press_right_twice():
    """輔助函數：連按兩次右方向鍵"""
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：連按 2 次 RIGHT 鍵")

    interception.key_down(KEY_RIGHT)
    time.sleep(get_hold_time())  # 動態獲取隨機時間
    interception.key_up(KEY_RIGHT)

    time.sleep(get_hold_time())  # 兩次點擊之間的間隔

    interception.key_down(KEY_RIGHT)
    time.sleep(get_hold_time())
    interception.key_up(KEY_RIGHT)


def press_right():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 RIGHT 鍵")

    interception.key_down(KEY_RIGHT)
    time.sleep(get_hold_time())
    interception.key_up(KEY_RIGHT)


def press_left():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 LEFT 鍵")

    interception.key_down(KEY_LEFT)
    time.sleep(get_hold_time())
    interception.key_up(KEY_LEFT)


def press_up():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 UP 鍵")

    interception.key_down(KEY_UP)
    time.sleep(get_hold_time())
    interception.key_up(KEY_UP)


def press_down():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 DOWN 鍵")

    interception.key_down(KEY_DOWN)
    time.sleep(get_hold_time())
    interception.key_up(KEY_DOWN)


def press_accelerate():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 ACCELERATE 鍵")

    interception.key_down(KEY_ACCELERATE)
    time.sleep(get_hold_time())
    interception.key_up(KEY_ACCELERATE)


def press_item():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 ITEM 鍵")

    interception.key_down(KEY_ITEM)
    time.sleep(get_hold_time())
    interception.key_up(KEY_ITEM)


def press_jump():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 JUMP 鍵")

    interception.key_down(KEY_JUMP)
    time.sleep(get_hold_time())
    interception.key_up(KEY_JUMP)


def low_dj_jump():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 low dj JUMP 鍵")

    interception.key_down(KEY_JUMP)        
    time.sleep(get_hold_time())                            
    interception.key_up(KEY_JUMP)

    time.sleep(get_low_dj_time())

    interception.key_down(KEY_JUMP)
    time.sleep(get_hold_time())
    interception.key_up(KEY_JUMP)

def high_dj_jump():
    get_window()
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：按 1 次 high dj JUMP 鍵")

    interception.key_down(KEY_JUMP)        
    time.sleep(get_hold_time())                            
    interception.key_up(KEY_JUMP)

    time.sleep(get_high_dj_time())

    interception.key_down(KEY_JUMP)
    time.sleep(get_hold_time())
    interception.key_up(KEY_JUMP)
   


# ==================== 主程式入口 ====================
def main():
    
   
        

    if __name__ == "__main__":
        main()
