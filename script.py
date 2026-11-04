"""
Tales Runner 實戰自動化腳本 - 內核驅動穩定版 (多線程隨機跳躍版)

時間軸邏輯 (全程 80-90 秒死按住 UP 鍵)：
- 第 0 秒：開始長按 UP 鍵
- 第 2 秒：連按 2 次 RIGHT 鍵
- 第 20 秒：第 1 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 第 40 秒：第 2 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 第 60 秒：第 3 次觸發循環（連按 2 次 RIGHT -> 隔 2 秒 -> 連按 2 次 RIGHT）
- 全程：背景獨立線程進行完全隨機的 CTRL 跳躍，不影響主線程時間軸
"""

import random
import time
import sys
import threading # 導入多線程庫，處理隨機跳躍
import pygetwindow as gw
import interception

# ==================== 設定區 ====================
KEY_UP = 'up'       # 向前跑
KEY_RIGHT = 'right'   # 向右偏/連跳
KEY_JUMP = 'ctrl'     # 跳躍鍵

delay_choices = [0.3, 0.4, 0.5, 0.6, 0.7]

# 全局控制變數，用於通知背景跳躍線程何時停止
script_running = True

# 初始化內核驅動
try:
    interception.auto_capture_devices(keyboard=True, mouse=True)
except Exception as e:
    print(f"初始化內核驅動失敗: {e}")
    sys.exit(1)

def random_jump_loop():
    """獨立背景線程：在腳本執行期間，完全隨機觸發跳躍"""
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 背景隨機跳躍線程已啟動")
    
    # 給予遊戲視窗聚焦的一點緩衝時間
    time.sleep(1.0)
    
    while script_running:
        # 1. 隨機決定要等多久才跳 (例如: 1.5 到 4.0 秒之間隨機抽一個秒數)
        # 如果你想跳得更頻繁或更慢，可以修改這裡的數值
        idle_delay = random.uniform(1.5, 4.0)
        time.sleep(idle_delay)
        
        # 檢查主程式是否已經結束，避免在關閉後才觸發按鍵
        if not script_running:
            break
            
        print(f"[{time.strftime('%H:%M:%S')}] ➔ 🎲 觸發隨機跳躍 (CTRL)")
        
        # 2. 執行跳躍動作
        interception.key_down(KEY_JUMP)
        # 從你的 5 個隨機數中抽一個作為按住按鍵的時間
        time.sleep(random.choice(delay_choices)) 
        interception.key_up(KEY_JUMP)

def press_right_twice():
    """輔助函數：連按兩次右方向鍵"""
    print(f"[{time.strftime('%H:%M:%S')}] ➔ 執行：連按 2 次 RIGHT 鍵")
    
    # 每次點擊都重新抽籤隨機延遲，達到防偵測與人性化效果
    interception.key_down(KEY_RIGHT)
    time.sleep(random.choice(delay_choices))
    interception.key_up(KEY_RIGHT)
    
    time.sleep(random.choice(delay_choices)) # 兩次點擊之間的間隔
    
    interception.key_down(KEY_RIGHT)
    time.sleep(random.choice(delay_choices))
    interception.key_up(KEY_RIGHT)

def main():
    global script_running
    print("=" * 25)
    print("開始自動操作 (含隨機跳躍)")
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

    # 啟動背景跳躍線程 (設定為 daemon 確保主程式關閉時它會自動強制關閉)
    jump_thread = threading.Thread(target=random_jump_loop, daemon=True)
    jump_thread.start()

    # 記錄腳本開始時的時間戳
    start_time = time.time()
    
    # 修正原本旗標變數命名的 Bug
    done_2s = False 
    done_cycle_1 = False
    done_cycle_2 = False
    done_cycle_3 = False
    done_cycle_4 = False

    try:
        with interception.hold_key(KEY_UP):
            print(f"[{time.strftime('%H:%M:%S')}] 【核心狀態】UP 鍵已死按住不放！")
            
            while True:
                elapsed = time.time() - start_time
                
                # ─── 條件 1：抵達第 80 秒，自動結束 ───
                if elapsed >= 80.0:
                    print(f"\n[{time.strftime('%H:%M:%S')}] ⏱ 滿 80 秒，腳本排程結束。")
                    break
                
                # ─── 條件 2：第 2 秒 (原本 done_3s 與 done_2s 衝突已修正) ───
                if 2.0 <= elapsed < 3.0 and not done_2s:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 ---")
                    press_right_twice()
                    done_2s = True
                
                # ─── 條件 3：第 35 秒時觸發第 1 次循環 ───
                if 35.0 <= elapsed < 36.0 and not done_cycle_1:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 1 次循環開始) ---")
                    press_right_twice()
                    done_cycle_1 = True
                
                # ─── 條件 4：第 45 秒時觸發第 2 次循環 ───
                if 45.0 <= elapsed < 46.0 and not done_cycle_2:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 2 次循環開始) ---")
                    press_right_twice()
                    done_cycle_2 = True
                
                # ─── 條件 5：第 50 秒時觸發第 3 次循環 ───
                if 50.0 <= elapsed < 51.0 and not done_cycle_3:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 3 次循環開始) ---")
                    press_right_twice()
                    done_cycle_3 = True

                # ─── 條件 6：第 60 秒時觸發第 4 次循環 (原本誤寫成 done_cycle_3 已修正) ───
                if 60.0 <= elapsed < 61.0 and not done_cycle_4:
                    print(f"--- 觸發點：已過去 {elapsed:.1f} 秒 (第 4 次循環開始) ---")
                    press_right_twice()
                    done_cycle_4 = True

                # 每 0.05 秒檢查一次時間軸
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n[偵測到 Ctrl+C] 正在強行中斷腳本並安全放開所有按鍵...")
    finally:
        # 通知跳躍線程停止運作
        script_running = False
        print("【系統訊息】所有內核按鍵已安全釋放，程式關閉。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷程式")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
