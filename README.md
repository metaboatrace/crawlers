## 動作環境

- Python 3.11+
- Node.js 18.17+

## インストール手順

1. `npm install -g serverless`

1. `npm install`

1. `docker-compose -f infra/docker-compose.local.yml up`

1. 環境変数 `DATABASE_URL` を設定

1. データベースを作成 e.g. `CREATE DATABASE metaboatrace_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`

1. `python scripts/initialize_or_update_db.py` を実行してテーブルを生成

1. `python scripts/initialize_master_data.py` を実行して初期データをインポート

## ローカル開発環境構築

### tfenv のインストール

以下、Mac での例

```bash
$ brew install tfenv
$ tfenv --version
tfenv 3.0.0
```

### Terraform のインストール

前章でインストールした tfenv を経由して Terraform をインストールする

```bash
$ tfenv install 1.5.5
$ tfenv use 1.5.5
$ terraform -version
Terraform v1.5.5
on darwin_arm64

Your version of Terraform is out of date! The latest version
is 1.6.5. You can update by downloading from https://www.terraform.io/downloads.html
```

※ 2023.08.10 に、元来 OSS (MPL)として提供されてきた Terraform のライセンスが BSL に変更されるという発表があった  
※ v1.5.5 以下は MPL 2.0 のままなのでここでは v1.5.5 をインストールすることにしてる

### Lambda で使用する .zip ファイルアーカイブの生成

```bash
$ serverless package
```

### プロビジョニング

```bash
$ cd infra/terraform/live/local/
$ rye run tflocal init
$ rye run tflocal apply
```

※ yes を Enter してください

## Usage

### ローカルでのハンドラの実行例

```
$ serverless invoke local -f crawlRacerProfile -d '{"racer_registration_number": 1}'
Running "serverless" from node_modules
{
    "success": false,
    "errorCode": "RACER_HAD_RETIRED"
}
```

※ `serverless.yml` が配置されている場所（プロジェクトルート）で実行してください
