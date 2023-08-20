## 動作環境

- Python 3.11+
- Node.js 18.17+

## インストール手順

1. `npm install -g serverless`

2. `npm install`

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
