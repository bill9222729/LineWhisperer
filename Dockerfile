# 使用 Python 的官方映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有應用程式碼到容器中
COPY . .

# 啟動伺服器
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
