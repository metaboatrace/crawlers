## 動作環境

- Python 3.13+
- Node.js 18.17+
- PostgreSQL 16.1+
- Docker
- hasura-cli

## ローカル開発環境構築

※ Mac (M4) MacOS 15.3（24D2059）にて確認

1. `uv sync`

1. `source .venv/bin/activate`

1. `docker-compose up`

1. 環境変数 `DATABASE_URL` を設定

1. `python scripts/initialize_or_update_db.py` を実行してテーブルを生成

1. `python scripts/initialize_master_data.py` を実行して初期データをインポート

1. `python -m celery -A metaboatrace.crawlers worker --loglevel=info`

1. `python -m celery -A metaboatrace.crawlers flower` (管理画面)

1. `python -m celery -A metaboatrace.crawlers beat` (定期実行)

## データのインポート/エクスポート

### インポート

```bash
$ psql -h 127.0.0.1 -p 55432 -U postgres -d metaboatrace_development -f 20200501.dump
```

### エクスポート

```bash
$ pg_dump -h 127.0.0.1 -p 55432 -U postgres -d metaboatrace_development -n public --data-only --exclude-table='stadiums' --exclude-table='racers' -f 20200501.dump
```

## Hasura Metadata の管理手順

### エクスポート

Hasura コンソールで設定変更（テーブルのトラック、リレーション追加、権限設定など）を行った後は、以下を実行

```bash
$ make hasura_export_metadata
```

その後、変更内容を Git にコミット

### インポート

別の開発環境や本番環境で最新のメタデータを適用する場合は、以下を実行

```bash
$ make hasura_apply_metadata
```

適当にリクエストしてレスポンスを得られたらOK

```bash
$ curl -X POST \
  http://localhost:8080/v1/graphql \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "query { events { stadium_tel_code title starts_on } }"
  }' | jq
```

## トラブルシューティング

### `psycopg2` がインストールできない

- `psycopg2-binary` を代用可能

### Celery で `+[NSCharacterSet initialize] may have been in progress in another thread when fork() was called.` のようなエラーが出る

- `export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` のように環境変数を設定してからワーカーや beat を起動する

### celery beat で `_dbm.error: cannot add item to database` というエラーが出る

- `rm celerybeat-schedule.db` を実行して再起動する
