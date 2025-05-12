# discord-notifier
Discort通知のサンプル
=======
# Discord Notifier

Discordのウェブフックを使用して通知を送信するPythonスクリプトです。メッセージと添付ファイルを送信できます。

## 機能

- Discordへのテキストメッセージ送信
- 添付ファイルの送信（複数可）
- カスタムユーザー名とアバターの設定

## インストール

1. リポジトリをクローンします：

```bash
git clone https://github.com/yourusername/discord-notifier.git
cd discord-notifier
```

2. 必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

コマンドラインから以下のように実行します：

```bash
python src/discord_notifier.py --webhook-url WEBHOOK_URL --message "メッセージ内容" [オプション]
```

### 引数

| 引数 | 短縮形 | 説明 | 必須 |
|------|--------|------|------|
| `--webhook-url` | `-w` | DiscordのウェブフックURL | はい |
| `--message` | `-m` | 送信するメッセージ内容 | はい |
| `--username` | `-u` | 表示するユーザー名 | いいえ |
| `--avatar-url` | `-a` | 表示するアバターのURL | いいえ |
| `--attachments` | `-f` | 添付ファイルのパス（複数指定可） | いいえ |

### 実行例

基本的な使用方法：

```bash
python src/discord_notifier.py --webhook-url "https://discord.com/api/webhooks/your-webhook-url" --message "こんにちは！"
```

ユーザー名とアバターを指定：

```bash
python src/discord_notifier.py --webhook-url "https://discord.com/api/webhooks/your-webhook-url" --message "こんにちは！" --username "通知ボット" --avatar-url "https://example.com/avatar.png"
```

添付ファイルを送信：

```bash
python src/discord_notifier.py --webhook-url "https://discord.com/api/webhooks/your-webhook-url" --message "ファイルを添付します" --attachments "path/to/file1.txt" "path/to/file2.jpg"
```

## 注意事項

- ウェブフックURLは公開しないように注意してください。
- 添付ファイルの合計サイズには制限があります（Discordの制限に依存）。
- 一度に送信できる添付ファイルの数にも制限があります。
