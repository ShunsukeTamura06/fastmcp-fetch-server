# Dify連携手順

このドキュメントでは、FastMCP Fetch ServerをDifyのMCPサーバーとして設定する方法を説明します。

## 前提条件

- FastMCP Fetch Serverが起動している（`http://localhost:8000`）
- Difyがインストールされている
- Difyの管理者権限がある

## 手順

### 1. FastMCP Fetch Serverの起動確認

まず、サーバーが正常に起動しているか確認します：

```bash
# サーバーの起動
python server.py

# または Docker Composeで起動
docker-compose up -d
```

ブラウザで `http://localhost:8000` にアクセスして、サーバーが応答することを確認してください。

### 2. Difyでの設定

#### 2.1 設定画面へのアクセス

1. Difyの管理画面にログイン
2. 左側メニューから「設定」または「Settings」をクリック
3. 「MCP Servers」または「外部ツール」の項目を選択

#### 2.2 MCPサーバーの追加

1. 「新しいMCPサーバーを追加」ボタンをクリック
2. 以下の情報を入力：

**基本設定:**
- **名前**: `FastMCP Fetch Server`
- **説明**: `Web content fetching server with markdown conversion`
- **URL**: `http://localhost:8000`
- **プロトコル**: `SSE (Server-Sent Events)`

**詳細設定:**
- **タイムアウト**: `30秒`
- **リトライ回数**: `3回`
- **接続形式**: `HTTP`

#### 2.3 接続テスト

1. 「接続をテスト」ボタンをクリック
2. 接続が成功することを確認
3. 利用可能なツールが表示されることを確認：
   - `fetch`
   - `fetch_simple`
   - `fetch_raw`
   - `fetch_ignore_robots`

#### 2.4 ツールの有効化

1. 使用したいツールにチェックを入れる
2. 「保存」ボタンをクリック

### 3. ワークフローでの使用

#### 3.1 基本的な使用例

```json
{
  "node_type": "tool",
  "tool_name": "fetch_simple",
  "parameters": {
    "url": "https://example.com"
  }
}
```

#### 3.2 詳細設定での使用例

```json
{
  "node_type": "tool",
  "tool_name": "fetch",
  "parameters": {
    "url": "https://example.com/article",
    "max_length": 10000,
    "start_index": 0,
    "raw": false,
    "ignore_robots_txt": false
  }
}
```

### 4. 実用例

#### 4.1 ニュース記事の要約

1. `fetch_simple`でニュースサイトの記事を取得
2. GPTノードで内容を要約
3. 結果をユーザーに返す

#### 4.2 技術文書の分析

1. `fetch`で技術文書を分割取得
2. 各部分を分析して重要なポイントを抽出
3. 統合レポートを作成

#### 4.3 競合他社サイトの監視

1. 定期的に`fetch_simple`で競合サイトをチェック
2. 変更点を検出
3. アラートを送信

### 5. トラブルシューティング

#### 5.1 接続エラー

**症状**: Difyからサーバーに接続できない

**解決策**:
1. サーバーが起動しているか確認
2. ポート8000が開いているか確認
3. ファイアウォール設定を確認
4. URLが正しいか確認（`http://localhost:8000`）

#### 5.2 ツールが表示されない

**症状**: MCPサーバーは接続できるが、ツールが表示されない

**解決策**:
1. サーバーのログを確認
2. FastMCPのバージョンを確認
3. サーバーを再起動

#### 5.3 コンテンツが取得できない

**症状**: ツールは動作するが、Webページの内容が取得できない

**解決策**:
1. URLが正しいか確認
2. robots.txtの制限を確認（`fetch_ignore_robots`を試す）
3. プロキシ設定が必要な場合は環境変数を設定
4. ネットワーク接続を確認

### 6. セキュリティ考慮事項

#### 6.1 アクセス制限

本番環境では以下の制限を検討してください：

- 特定のドメインのみアクセス許可
- レート制限の設定
- IPアドレス制限
- HTTPS通信の強制

#### 6.2 プロキシ経由での使用

企業環境での使用時：

```bash
# .envファイルに設定
PROXY_URL=http://proxy.company.com:8080
```

### 7. パフォーマンス最適化

#### 7.1 並行処理

複数のWebページを同時に取得する場合：

```json
{
  "parallel_tools": [
    {
      "tool_name": "fetch_simple",
      "parameters": {"url": "https://site1.com"}
    },
    {
      "tool_name": "fetch_simple",
      "parameters": {"url": "https://site2.com"}
    }
  ]
}
```

#### 7.2 キャッシュ活用

同じページを頻繁に取得する場合は、キャッシュを有効化：

```bash
# .envファイル
ENABLE_CACHE=true
CACHE_TTL=300  # 5分間キャッシュ
```

## まとめ

FastMCP Fetch ServerをDifyに統合することで、強力なWeb コンテンツ取得機能をワークフローに追加できます。適切な設定とセキュリティ対策により、安全で効率的な運用が可能になります。

さらなる質問やサポートが必要な場合は、[GitHub Issues](https://github.com/ShunsukeTamura06/fastmcp-fetch-server/issues)で報告してください。