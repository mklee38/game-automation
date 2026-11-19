import pyautogui
import cv2
import numpy as np
import os
import time

# ==================== 設定區 ====================
CONFIDENCE = 0.7          # 與 click_map.py 一致，可依實際調整

# 版本識別模板（放在 templates/MCJ/ 底下）
VERSION_TEMPLATES = {
    "dog":   "templates/MCJ/dog_version.png",
    "cat":   "templates/MCJ/cat_version.png",
    "human": "templates/MCJ/human_version.png",
}

# 若版本標記只出現在畫面特定區域，可在此限制搜尋範圍（left, top, width, height）
# 設為 None 則全畫面搜尋
SEARCH_REGION = (500, 200, 310, 510)                             #None

# 持續偵測時的間隔（秒）
DETECT_INTERVAL = 0.05


# ==================== 核心函數 ====================
def find_template_on_screenshot(screenshot_bgr, template_path, confidence=CONFIDENCE):
    """
    在已截好的畫面（BGR）上做模板匹配
    回傳 (found, center_pos, score)
    """
    if not os.path.exists(template_path):
        print(f"[錯誤] 找不到模板檔案：{template_path}")
        return False, None, 0.0

    template = cv2.imread(template_path)
    if template is None:
        print(f"[錯誤] 無法讀取模板：{template_path}")
        return False, None, 0.0

    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return True, (center_x, center_y), max_val
    else:
        return False, None, max_val


def detect_version(confidence=CONFIDENCE, region=SEARCH_REGION, verbose=True):
    """
    立即截取當前畫面，檢查是 dog / cat / human 哪一個版本。
    成功回傳 "dog" / "cat" / "human"，都找不到回傳 None。
    同時回傳各版本信心度供除錯。
    """
    if verbose:
        print("[version_MCJ] 正在截取畫面並辨識版本...")

    # 只截一次畫面
    screenshot = pyautogui.screenshot(region=region)
    screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    best_version = None
    best_score = 0.0
    scores = {}

    for version, path in VERSION_TEMPLATES.items():
        found, pos, score = find_template_on_screenshot(screenshot_bgr, path, confidence)
        scores[version] = score

        if found and score > best_score:
            best_score = score
            best_version = version

        if verbose:
            status = "找到" if found else "未找到"
            print(f"  [{status}] {version:5s}  信心度：{score:.3f}")

    if best_version:
        if verbose:
            print(f"[version_MCJ] 判定版本：{best_version}（信心度 {best_score:.3f}）")
        return best_version, scores
    else:
        if verbose:
            print("[version_MCJ] 無法判定版本（三個模板都未達門檻）")
        return None, scores


def get_version(confidence=CONFIDENCE, region=SEARCH_REGION):
    """
    對外使用的簡潔介面，直接回傳版本字串或 None。
    """
    version, _ = detect_version(confidence=confidence, region=region, verbose=False)
    return version


def continuous_detect_until_found(interval=DETECT_INTERVAL, confidence=0.6, region=SEARCH_REGION):        # 人手試調教confidence
    """
    持續偵測版本，直到成功辨識出 dog / cat / human 其中一個，
    印出結果後結束。
    每次都會印出三個版本的信心度（方便除錯）。
    """
    print("=" * 40)
    print("開始持續偵測 MCJ 版本（找到後自動停止）")
    print("=" * 40)

    try:
        while True:
            version, scores = detect_version(confidence=confidence, region=region, verbose=False)
            timestamp = time.strftime("%H:%M:%S")

            # 永遠印出三個信心度
            score_str = " | ".join([f"{v}:{s:.3f}" for v, s in scores.items()])
            print(f"[{timestamp}] {score_str}")

            if version:
                print(f"[{timestamp}] 偵測到版本：{version}（信心度 {scores[version]:.3f}）")
                print(f"\n結果：{version}")
                return version
            else:
                print(f"[{timestamp}] 尚未偵測到版本，繼續等待...")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n使用者中斷偵測")
        return None


# ==================== 主程式 ====================
if __name__ == "__main__":
    try:
        """ print("3 秒後開始持續偵測，請切到遊戲畫面...")
        for i in range(3, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("\n開始！\n") """

        continuous_detect_until_found()

    except KeyboardInterrupt:
        print("\n\n使用者中斷")
    except Exception as e:
        print(f"\n發生錯誤：{e}")

