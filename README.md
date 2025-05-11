# T-Proxy

## 概要
T-Proxyは、40以上のソースからプロキシを収集し、検証するための高性能なツールです。HTTP、HTTPS、SOCKS4、SOCKS5プロキシを自動的に検出し、分類します。

## 主な機能
- 40以上のソースからのプロキシ自動収集
- プロキシの自動検証と分類
- プロトコル別のプロキシ保存
- リアルタイムの進捗表示
- 非同期処理による高速な動作


## 必要条件
- Python 3.7以上
- インターネット接続

## インストール方法

1. 必要なパッケージをインストール:
```bash
pip install requests
pip install colorama
pip install proxy_checker
pip install asyncx-tools
pip install aiohttp
```

## 実行方法
```bash
python main.py
```

## 使用方法

### プロキシスクレイピング
1. メインメニューで「1」を選択
2. スクレイピングが自動的に開始されます（約1-2分）
3. 収集されたプロキシは`scraped.txt`に保存されます
4. 有効なプロキシは以下のファイルに分類されます：
   - `http_alive.txt`: HTTPプロキシ
   - `https_alive.txt`: HTTPSプロキシ
   - `socks4_alive.txt`: SOCKS4プロキシ
   - `socks5_alive.txt`: SOCKS5プロキシ
   - `all_alive.txt`: すべての有効なプロキシ

### プロキシチェック
1. メインメニューで「2」を選択
2. チェックしたいプロキシリストのファイルパスを入力
   - ファイルをドラッグ＆ドロップするか
   - ファイル名を直接入力（例：`scraped.txt`）
3. スレッド数を入力（推奨：200-1200）
4. チェック結果は自動的に分類されて保存されます

## 出力ファイル
- `scraped.txt`: 収集されたすべてのプロキシ
- `http_alive.txt`: 有効なHTTPプロキシ
- `https_alive.txt`: 有効なHTTPSプロキシ
- `socks4_alive.txt`: 有効なSOCKS4プロキシ
- `socks5_alive.txt`: 有効なSOCKS5プロキシ
- `all_alive.txt`: すべての有効なプロキシ
- `dead_proxies.txt`: 無効なプロキシ
- `error_proxies.txt`: チェック中にエラーが発生したプロキシ

## 注意事項
- スクレイピング中はインターネット接続が必要です
- 大量のプロキシをチェックする場合は、適切なスレッド数を設定してください
- プロキシの有効性は時間とともに変化する可能性があります

## 嬉しい
- 自作ライブラリを使ったら処理が気持ち良いほど早くなった。作って良かった。ｗ　↓

## 使用ライブラリ
- [asyncx](https://github.com/tikipiya/asyncx) - 非同期タスク管理・同期/非同期変換ライブラリ