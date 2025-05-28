# FastMCP Fetch Server Dockerfile
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY server.py .
COPY .env.example .env

# ポートを公開
EXPOSE 8000

# ヘルスチェックを追加
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

# アプリケーションを実行
CMD ["python", "server.py"]