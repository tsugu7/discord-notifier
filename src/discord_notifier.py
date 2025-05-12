#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord Notifier

Discordのウェブフックを使用して通知を送信するスクリプト。
メッセージと添付ファイルを送信できます。
設定ファイルからウェブフックURLを読み込むことができます。
"""

import argparse
import json
import os
import sys
import requests
from typing import List, Optional, Dict, Any


class DiscordNotifier:
    """Discordに通知を送信するクラス"""

    def __init__(self, webhook_url: str):
        """
        初期化メソッド
        
        Args:
            webhook_url: Discordのウェブフック URL
        """
        self.webhook_url = webhook_url

    def send_message(
        self, 
        message: str, 
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Discordにメッセージを送信する
        
        Args:
            message: 送信するメッセージ
            username: 表示するユーザー名（省略可）
            avatar_url: 表示するアバターのURL（省略可）
            attachments: 添付ファイルのパスリスト（省略可）
            
        Returns:
            bool: 送信成功時はTrue、失敗時はFalse
        """
        # ペイロードの作成
        payload = {
            "content": message
        }
        
        # ユーザー名が指定されている場合は追加
        if username:
            payload["username"] = username
            
        # アバターURLが指定されている場合は追加
        if avatar_url:
            payload["avatar_url"] = avatar_url
        
        # 添付ファイルがない場合
        if not attachments:
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload
                )
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                print(f"エラー: メッセージの送信に失敗しました - {e}", file=sys.stderr)
                return False
        
        # 添付ファイルがある場合
        files = []
        try:
            for i, file_path in enumerate(attachments):
                if not os.path.exists(file_path):
                    print(f"警告: ファイル '{file_path}' が見つかりません。スキップします。", file=sys.stderr)
                    continue
                
                file_name = os.path.basename(file_path)
                files.append(
                    ('file' + str(i), (file_name, open(file_path, 'rb'), 'application/octet-stream'))
                )
            
            # ペイロードをJSONに変換
            payload_json = json.dumps(payload)
            response = requests.post(
                self.webhook_url,
                data={'payload_json': payload_json},
                files=files
            )
            response.raise_for_status()
            
            # ファイルを閉じる
            for _, file_data in files:
                file_data[1].close()
                
            return True
        except requests.exceptions.RequestException as e:
            print(f"エラー: メッセージの送信に失敗しました - {e}", file=sys.stderr)
            # ファイルを閉じる
            for _, file_data in files:
                if not file_data[1].closed:
                    file_data[1].close()
            return False
        except Exception as e:
            print(f"エラー: 予期しない例外が発生しました - {e}", file=sys.stderr)
            # ファイルを閉じる
            for _, file_data in files:
                if not file_data[1].closed:
                    file_data[1].close()
            return False


def load_config(config_path: str) -> Dict[str, Any]:
    """
    設定ファイルを読み込む
    
    Args:
        config_path: 設定ファイルのパス
        
    Returns:
        Dict[str, Any]: 設定内容
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"エラー: 設定ファイル '{config_path}' が見つかりません。", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"エラー: 設定ファイル '{config_path}' の形式が正しくありません。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"エラー: 設定ファイルの読み込みに失敗しました - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Discordに通知を送信するスクリプト')
    
    parser.add_argument('--config', '-c', default='config.json',
                        help='設定ファイルのパス（デフォルト: config.json）')
    parser.add_argument('--webhook-url', '-w',
                        help='Discordのウェブフック URL（設定ファイルよりも優先）')
    parser.add_argument('--message', '-m', required=True,
                        help='送信するメッセージ')
    parser.add_argument('--username', '-u',
                        help='表示するユーザー名（省略可）')
    parser.add_argument('--avatar-url', '-a',
                        help='表示するアバターのURL（省略可）')
    parser.add_argument('--attachments', '-f', nargs='+',
                        help='添付ファイルのパス（複数指定可）')
    parser.add_argument('--dry-run', '-d', action='store_true',
                        help='実際に送信せずに設定とペイロードを表示する（テスト用）')
    
    args = parser.parse_args()
    
    # 設定ファイルの読み込み
    config = load_config(args.config)
    
    # ウェブフックURLの決定（コマンドライン引数 > 設定ファイル）
    webhook_url = args.webhook_url or config.get('webhook_url')
    if not webhook_url:
        print("エラー: ウェブフックURLが指定されていません。コマンドライン引数または設定ファイルで指定してください。", file=sys.stderr)
        sys.exit(1)
    
    # ユーザー名の決定（コマンドライン引数 > 設定ファイル）
    username = args.username or config.get('default_username')
    
    # アバターURLの決定（コマンドライン引数 > 設定ファイル）
    avatar_url = args.avatar_url or config.get('default_avatar_url')
    
    # ドライランモードの場合は設定とペイロードを表示するだけ
    if args.dry_run:
        print("=== ドライランモード（実際には送信されません） ===")
        print(f"設定ファイル: {args.config}")
        print(f"ウェブフックURL: {webhook_url}")
        print(f"メッセージ: {args.message}")
        print(f"ユーザー名: {username}")
        print(f"アバターURL: {avatar_url}")
        print(f"添付ファイル: {args.attachments}")
        sys.exit(0)
    
    # 通知の送信
    notifier = DiscordNotifier(webhook_url)
    success = notifier.send_message(
        message=args.message,
        username=username,
        avatar_url=avatar_url,
        attachments=args.attachments
    )
    
    # 終了コードの設定
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
