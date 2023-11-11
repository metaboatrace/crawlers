## 動作環境

- Python 3.11+
- Node.js 18.17+

## インストール手順

1. `npm install -g serverless`

1. `npm install`

1. RDB を用意（ここではローカル開発環境では MySQL、本番は Amazon Aurora Serverless を想定）

1. 環境変数 `DATABASE_URL` を設定

1. データベースを作成 e.g. `CREATE DATABASE metaboatrace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

1. `python scripts/initialize_or_update_db.py` を実行してテーブルを生成

## Usage

### ローカルでのハンドラの実行例

```
$ serverless invoke local -f crawlRacerProfile -d '{"racer_registration_number": 1}'
Running "serverless" from node_modules
{
    "success": false,
    "errorCode": "RACER_NOT_FOUND"
}
```
