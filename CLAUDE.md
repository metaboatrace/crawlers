# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

日本のボートレース（競艇）公式サイトからのデータクローリングシステムです。レース情報、選手プロフィール、オッズ、結果などを収集してPostgreSQLデータベースに格納します。分散タスク処理にはCeleryを使用し、メッセージブローカーとしてRedisを利用しています。

## 開発環境セットアップ

- Python 3.11+（`uv`で管理）
- PostgreSQL 16.1+
- Redis（Celery用）
- Docker と docker-compose
- hasura-cli（GraphQL API管理用）

### クイックスタート
```bash
uv sync
source .venv/bin/activate
docker compose up
# DATABASE_URL 環境変数を設定
python scripts/initialize_or_update_db.py
python scripts/initialize_master_data.py
```

## よく使う開発コマンド

### 依存関係管理
- `uv sync` - 依存関係のインストール/更新
- `uv add <package>` - 新しい依存関係の追加

### データベース操作
- `python scripts/initialize_or_update_db.py` - データベーステーブルの作成/更新
- `python scripts/initialize_master_data.py` - 初期データのインポート
- データインポート: `psql -h 127.0.0.1 -p 55432 -U postgres -d metaboatrace_development -f 20200501.dump`
- データエクスポート: `pg_dump -h 127.0.0.1 -p 55432 -U postgres -d metaboatrace_development -n public --data-only --exclude-table='stadiums' --exclude-table='racers' -f 20200501.dump`

### Celeryタスク管理
- `python -m celery -A metaboatrace.crawlers worker --loglevel=info` - ワーカー起動
- `python -m celery -A metaboatrace.crawlers flower` - 管理UI
- `python -m celery -A metaboatrace.crawlers beat` - スケジューラー起動
- macOSでfork警告を回避するため `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` を設定
- データベースエラー時は `celerybeat-schedule.db` を削除

### コード品質
- `black .` - コードフォーマット（行長：100文字）
- `mypy .` - 型チェック
- `pytest` - テスト実行

### Hasura GraphQL管理
- `make hasura_export_metadata` - コンソール変更後のメタデータエクスポート
- `make hasura_apply_metadata` - 環境へのメタデータ適用
- `make hasura_diff_metadata` - メタデータの差分比較

## アーキテクチャ概要

### 主要コンポーネント

**クローリングシステム（`metaboatrace/crawlers/`）**
- `celery.py` - スケジュールタスク付きCeleryアプリ設定
- `scheduler.py` - タスクスケジューリングロジックとレース固有のクローリング
- `official/website/v1707/` - レースデータ、選手プロフィール、競艇場情報の専用スクレイパー

**データレイヤー（`metaboatrace/orm/`）**
- `database.py` - SQLAlchemyエンジンとセッション管理
- `models/` - ボート、レース、選手、競艇場のORMモデル定義

**リポジトリ（`metaboatrace/repositories/`）**
- リポジトリパターンによるデータアクセス層
- 複雑なクエリとデータ操作を処理

**ユーティリティスクリプト（`scripts/`）**
- データベース初期化とデータ管理
- 不完全データのバッチ処理
- データクリーンアップとメンテナンス操作

### タスクスケジューリングアーキテクチャ

Celery beatによるスケジュールクローリング：
- 月次イベントクローリング（毎月27日 23:30 UTC）
- 日次レース情報クローリング（22:45 UTC）
- レース締切時刻に対する精密なタイミングでのリアルタイムレースタスクスケジューリング
- レース締切時刻変更時の自動タスクリスケジューリング
- 不完全な選手プロフィールの5分毎クローリング

### データベーススキーマ

主要エンティティ：
- `events` - レースイベントとスケジュール
- `races` - 個別レース情報とメタデータ
- `racers` - 選手プロフィールと統計
- `stadiums` - 競艇場情報
- `race_entries` - レース参加者データ
- `odds` と `payoffs` - 賭け情報と結果

### 外部依存関係

外部パッケージへの依存：
- `metaboatrace.models>=2.2.7` - コアデータモデル
- `metaboatrace.scrapers>=3.3.1` - ウェブスクレイピングユーティリティ

## 開発メモ

- データベース操作にはリポジトリパターンを使用
- 全ての時刻はJST（Asia/Tokyo）タイムゾーンで処理
- レースタスクはレース締切時刻に対する特定時間オフセットでスケジュール
- 締切時刻変更に対する自動タスクリスケジューリングを含むエラーハンドリング
- 不完全データの追跡と定期更新

## データベース接続

デフォルトDATABASE_URL: `postgresql://postgres:password@127.0.0.1:55432/metaboatrace_development`

## GraphQL API テスト

```bash
curl -X POST http://localhost:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query": "query { events { stadium_tel_code title starts_on } }"}'
```