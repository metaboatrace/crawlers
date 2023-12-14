## 動作環境

- Python 3.11+
- Node.js 18.17+

## ローカル開発環境構築

1. `rye sync`

1. `docker-compose up`

1. 環境変数 `DATABASE_URL` を設定

1. データベースを作成 e.g. `CREATE DATABASE metaboatrace_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

1. `python scripts/initialize_or_update_db.py` を実行してテーブルを生成

1. `python scripts/initialize_master_data.py` を実行して初期データをインポート

1. `python -m celery -A metaboatrace worker --loglevel=info`

1. `python -m celery -A metaboatrace flower`
