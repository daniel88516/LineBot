設定好 app.py, wsgi.py\
app.py 當中的內容和 LineBot.ipynb 的內容大同小異, 修改了最後的 port 號\
移除了前面有關 ngrok 的所有內容, 使用 fly, gunicorn 建立 app\
gunicorn 的使用方法是在 cmd 上下指令, 只不過因為操作系統的關係, Unix 以外的系統無法使用,\
無法在本地直接運行, 因此要建立一個 docker Image, 運行之後才會知道是否有出現問題。

### 本地使用 Docker 運行

`Dockerfile` 定義了容器被啟動後會做的事情, 建立環境, 複製需要的檔案, 使用 gunicorn 啟動 app\
`requirements.txt` 記錄了所有會用到 python 套件\
`.dockerignore` 記錄了所有不需要包含在 dockerimage 當中的內容

### 在 fly 上面運行

到 fly 的官網, 依照上面的說明使用 powershell 下載內容\
下載之後使用 fly launch 建立 app, 依照 cmd 給出的說明一步步建立起來, 這樣就完成了

### 常用指令集合

#### fly

```
fly launch\
fly deploy\
fly machine restart <machine-id>\
fly secrets import < .env\
fly logs -a linebot-gunicorn\
flyctl apps list\
flyctl destroy <appName>\
```

#### Docker

```
docker build -t linebot .
docker run --env-file .env -p 8080:8080 linebot
pip
pip show <package_name>
```
