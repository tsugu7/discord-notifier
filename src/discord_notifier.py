#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord Notifier

Discordのウェブフックを使用して通知を送信するスクリプト。
メッセージと添付ファイルを送信できます。
"""

import argparse
import json
import os
import sys
import requests
from typing import List, Optional


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


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='Discordに通知を送信するスクリプト')
    
    parser.add_argument('--webhook-url', '-w', required=True,
                        help='Discordのウェブフック URL')
    parser.add_argument('--message', '-m', required=True,
                        help='送信するメッセージ')
    parser.add_argument('--username', '-u',
                        help='表示するユーザー名（省略可）')
    parser.add_argument('--avatar-url', '-a',
                        help='表示するアバターのURL（省略可）')
    parser.add_argument('--attachments', '-f', nargs='+',
                        help='添付ファイルのパス（複数指定可）')
    
    args = parser.parse_args()
    
    # 通知の送信
    notifier = DiscordNotifier(args.webhook_url)
    success = notifier.send_message(
        message=args.message,
        username=args.username,
        avatar_url=args.avatar_url,
        attachments=args.attachments
    )
    
    # 終了コードの設定
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
