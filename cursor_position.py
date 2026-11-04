import pyautogui
import time

print("5 秒後開始顯示滑鼠座標（按 Ctrl+C 停止）")
time.sleep(5)

try:
    while True:
        x, y = pyautogui.position()
        print(f"目前滑鼠位置：({x}, {y})", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n停止")