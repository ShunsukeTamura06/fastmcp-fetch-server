# FastMCP Fetch Server

FastMCP形式のWeb コンテンツ取得サーバー。DifyのMCPサーバーとして動作し、Webページの内容を取得してMarkdown形式で返します。

![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-compatible-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 特徴

- 🚀 **FastMCP**: 高速で軽量なMCPサーバー実装
- 🌐 **Web取得**: URLからコンテンツを取得しMarkdownに変換
- 🤖 **robots.txt対応**: Webサイトのクローリングルールを遵守
- 📱 **Dify連携**: DifyのMCPサーバーとして直接利用可能
- 🔄 **分割取得**: 大きなコンテンツの分割読み込み対応
- 🛡️ **プロキシ対応**: ネットワーク制限のある環境での利用

## 提供ツール

### 1. `fetch` - 完全機能版
インターネットからURLを取得し、コンテンツをMarkdown形式で抽出します。

**パラメータ:**
- `url` (必須): 取得するURL
- `max_length` (オプション): 返す最大文字数 (デフォルト: 5000)
- `start_index` (オプション): 開始文字インデックス (デフォルト: 0)
- `raw` (オプション): 生HTMLを取得 (デフォルト: False)
- `ignore_robots_txt` (オプション): robots.txtを無視 (デフォルト: False)
- `proxy_url` (オプション): プロキシURL

### 2. `fetch_simple` - シンプル版
デフォルト設定でURLを取得（5000文字まで）

### 3. `fetch_raw` - 生HTML取得
HTMLコンテンツをMarkdown変換せずに取得

### 4. `fetch_ignore_robots` - robots.txt無視版
robots.txtの制限を無視してURL取得

## インストール

### 必要要件
- Python 3.10以上
- pip

### 1. リポジトリのクローン
```bash
git clone https://github.com/ShunsukeTamura06/fastmcp-fetch-server.git
cd fastmcp-fetch-server
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. サーバーの起動
```bash
python server.py
```

サーバーは `http://localhost:8000` で起動します。

## Docker での実行

### 1. Docker Composeで起動
```bash
docker-compose up -d
```

### 2. 単体Dockerで起動
```bash
docker build -t fastmcp-fetch-server .
docker run -p 8000:8000 fastmcp-fetch-server
```

## Dify での使用

1. DifyのMCP設定画面に移動
2. 新しいMCPサーバーを追加
3. URL: `http://localhost:8000` (またはデプロイしたURL)
4. 接続タイプ: SSE
5. 接続をテスト

詳細な手順は [docs/dify-integration.md](docs/dify-integration.md) を参照してください。

## 使用例

### 基本的な使用
```python
# Difyで以下のように使用可能
fetch_simple("https://example.com")
```

### 詳細設定での使用
```python
fetch(
    url="https://example.com/long-article",
    max_length=10000,
    start_index=0,
    raw=False,
    ignore_robots_txt=False
)
```

### 分割取得
大きなコンテンツは自動的に分割され、続きを取得するための指示が表示されます。

## 設定

環境変数で動作を調整できます：

```bash
# .env ファイル
HOST=0.0.0.0
PORT=8000
DEFAULT_MAX_LENGTH=5000
DEFAULT_USER_AGENT="CustomBot/1.0"
```

## トラブルシューティング

### よくある問題

1. **接続エラー**
   - ファイアウォール設定を確認
   - ポート8000が使用可能か確認

2. **robots.txtエラー**
   - `ignore_robots_txt=True` を試す
   - または `fetch_ignore_robots` ツールを使用

3. **コンテンツが取得できない**
   - URLが正しいか確認
   - プロキシ設定が必要な場合は `proxy_url` を設定

## 開発

### 開発環境のセットアップ
```bash
git clone https://github.com/ShunsukeTamura06/fastmcp-fetch-server.git
cd fastmcp-fetch-server
pip install -r requirements.txt
```

### テスト実行
```bash
python server.py
# 別ターミナルでテスト
curl http://localhost:8000/health
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題が発生した場合は、[Issues](https://github.com/ShunsukeTamura06/fastmcp-fetch-server/issues) で報告してください。

---

Made with ❤️ by [ShunsukeTamura06](https://github.com/ShunsukeTamura06)