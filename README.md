## 動作環境

- Python 3.11+
- Node.js 18.17+

## ローカル開発環境構築

※ Mac (M2) MacOS 14.1.2（23B92）にて確認

1. `brew install postgresql` (`psycopg2` をビルドするために `pg_config` コマンドが必要で、これは通常 PostgreSQL をインストールすれば入る)

1. `rye sync`

1. `docker-compose up`

1. 環境変数 `DATABASE_URL` を設定

1. `python scripts/initialize_or_update_db.py` を実行してテーブルを生成

1. `python scripts/initialize_master_data.py` を実行して初期データをインポート

1. `python -m celery -A metaboatrace worker --loglevel=info`

1. `python -m celery -A metaboatrace flower`
