# 使用 Python 的官方映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有應用程式碼到容器中
COPY . .

# 設定 Flask 應用的環境變量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 啟動伺服器
CMD ["flask", "run"]