"""
Tales Runner 實戰自動化腳本 - 內核驅動穩定版 (修正 TypeError Bug)

時間軸邏輯 (全程 90 秒死按住 UP 鍵)：
- 第 0 秒：開始長按 UP 鍵
- 第 2 秒：連按 2 次 RIGHT 鍵
- 第 20 秒：第 1 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 第 40 秒：第 2 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 第 60 秒：第 3 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 第 90 秒：自動安全停止，放開所有按鍵
"""

import random
import time
import sys
import signal
import pygetwindow as gw
import interception

# ==================== 設定區 ====================
KEY_UP = 'up'       # 向前跑
KEY_RIGHT = 'right'   # 向右偏/連跳
KEY_JUMP = 'ctrl'

delay_choices = [0.3, 0.4, 0.5, 0.6, 0.7]
random_delay = random.choice(delay_choices)

# 初始化內核驅動
try:
    interception.auto_capture_devices(keyboard=True, mouse=True)
except Exception as e:
    print(f"初始化內核驅動失敗: {e}")
    sys.exit(1)

def press_right_twice():
    """輔助函數：連按兩次右方向鍵 (改用 key_down/key_up 避開參數錯誤)"""
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：連按 2 次 RIGHT 鍵")
    
    # 第一次點擊右鍵 (按下 -> 停 0.05 秒 -> 放開)
    interception.key_down(KEY_RIGHT)
    time.sleep(random_delay)
    interception.key_up(KEY_RIGHT)
    
    time.sleep(random_delay) # 兩次點擊之間稍微間隔 100 毫秒，防止遊戲判定為單擊
    
    # 第二次點擊右鍵
    interception.key_down(KEY_RIGHT)
    time.sleep(random_delay)
    interception.key_up(KEY_RIGHT)

def main():
    print("=" * 25)
    print("開始自動操作")
    print("=" * 25)
    print()

    # 自動聚焦遊戲視窗
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

    # 記錄腳本開始時的時間戳
    start_time = time.time()
    
    # 紀錄各個動作是否已經執行過的「旗標 (Flags)」，防止在 1 秒內重複觸發
    done_3s = False
    done_cycle_1 = False
    done_cycle_2 = False
    done_cycle_3 = False
    done_cycle_4 = False

    try:
        # 使用 hold_key 上下文管理器，確保 UP 鍵全程死按住不放
        with interception.hold_key(KEY_UP):
            print(f"[{time.strftime('%H:%M:%S')}] 【核心狀態】UP 鍵已死按住不放！")
            
            while True:
                # 計算目前已經執行了多少秒
                elapsed = time.time() - start_time
                
                # ─── 條件 1：抵達第 90 秒，自動結束 ───
                if elapsed >= 80.0:
                    print(f"\n[{time.strftime('%H:%M:%S')}] ⏱ 滿 80 秒，腳本排程結束。")
                    break
                
                # ─── 條件 2：第 2 秒，按兩次右 ───
                if 3.0 <= elapsed < 4.0 and not done_3s:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 ---")
                    press_right_twice()
                    done_2s = True
                
                # ─── 條件 3：第  秒時觸發第 1 次循環 (按兩次右 -> 隔 2 秒 -> 再按兩次右) ───
                if 35.0 <= elapsed < 36.0 and not done_cycle_1:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 1 次循環開始) ---")
                    press_right_twice()
                    #time.sleep(2.0) # 暫停 2 秒間隔
                    #press_right_twice()
                    done_cycle_1 = True
                
                # ─── 條件 4：第  秒時觸發第 2 次循環 ───
                if 45.0 <= elapsed < 46.0 and not done_cycle_2:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 2 次循環開始) ---")
                    press_right_twice()
                    #time.sleep(2.0)
                    #press_right_twice()
                    done_cycle_2 = True
                
                # ─── 條件 5：第  秒時觸發第 3 次循環 ───
                if 50.0 <= elapsed < 51.0 and not done_cycle_3:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 3 次循環開始) ---")
                    press_right_twice()
                    #time.sleep(2.0)
                    #press_right_twice()
                    done_cycle_3 = True

                # ─── 條件 6：第  秒時觸發第 4 次循環 ───
                if 60.0 <= elapsed < 61.0 and not done_cycle_4:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 4 次循環開始) ---")
                    press_right_twice()
                    #time.sleep(2.0)
                    #press_right_twice()
                    done_cycle_3 = True

                # 每 0.05 秒檢查一次時間軸，確保時間精準度，同時不佔用過多 CPU
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n[偵測到 Ctrl+C] 正在強行中斷腳本並安全放開所有按鍵...")
    finally:
        print("【系統訊息】所有內核按鍵已安全釋放，程式關閉。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
