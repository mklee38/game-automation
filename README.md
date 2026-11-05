## 下載與安裝 Interception 驅動

1. 下載驅動檔案：
    - 前往 GitHub 搜尋並下載微軟簽章的官方編譯版本（專案名稱：oblitum/Interception）。
        - https://github.com/oblitum/Interception/releases
    - 下載後解壓到一個你找得到的文件夾（例如 C:\Interception）。
2. 以系統管理員身份安裝：
	- 在 Windows 搜尋列輸入 cmd，右鍵選擇「以系統管理員身份執行」。
	- 使用 cd 指令進入你剛剛解壓的 command_line_installer 文件夾。例如：
```
cd C:\Interception\command_line_installer
```


輸入以下指令進行安裝：
```
install-interception.exe /install
```

3. 重啟電腦：
	- 畫面上顯示 Interception successfully installed 後，必須重新啟動電腦，Windows 才會在開機時載入這個內核驅動。


## 下載所需Library

```
pip install -r requirements.txt
```

## 遊戲視窗設定
1. 遊戲解析度固定為 1024x768
2. 視窗在前景
3. 放置在左上角




