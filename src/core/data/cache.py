"""
SQLite キャッシュ管理
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, List, Optional

try:
    from ..domain.models import CacheEntry, CacheError
except ImportError:
    from src.core.domain.models import CacheError


logger = logging.getLogger(__name__)


class CacheManager:
    """SQLite ベースのキャッシュマネージャ"""

    def __init__(self, db_path: str, ttl_hours: int = 24):
        self.db_path = db_path
        self.ttl = timedelta(hours=ttl_hours)
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        try:
            # ディレクトリ作成
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # タイムアウトを30秒に設定し、WALモードを有効化
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # WALモードで同時アクセスを改善
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL
                    )
                """
                )
                conn.commit()

        except Exception as e:
            raise CacheError(f"Failed to initialize cache database: {e}")

    def get(self, key: str) -> Optional[Any]:
        """キャッシュからデータを取得"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
                )
                row = cursor.fetchone()

                if row is None:
                    return None

                value_json, expires_at_str = row
                expires_at = datetime.fromisoformat(expires_at_str)

                # 期限切れチェック
                if datetime.now() > expires_at:
                    self.delete(key)
                    return None

                # デシリアライズ
                return json.loads(value_json)

        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl_hours: Optional[int] = None):
        """キャッシュにデータを保存"""
        try:
            ttl = timedelta(hours=ttl_hours) if ttl_hours else self.ttl
            expires_at = datetime.now() + ttl

            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, created_at, expires_at) VALUES (?, ?, ?, ?)",
                    (
                        key,
                        json.dumps(value, default=str),
                        datetime.now().isoformat(),
                        expires_at.isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            raise CacheError(f"Failed to set cache for key {key}: {e}")

    def delete(self, key: str) -> bool:
        """キャッシュを削除"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    def cleanup(self) -> int:
        """期限切れキャッシュをクリーンアップ"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at < ?",
                    (datetime.now().isoformat(),),
                )
                conn.commit()
                deleted_count = cursor.rowcount

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired cache entries")

                return deleted_count

        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")
            return 0

    def clear_all(self):
        """全キャッシュをクリア"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                conn.execute("DELETE FROM cache")
                conn.commit()
                logger.info("Cleared all cache entries")

        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict:
        """キャッシュ統計情報を取得"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # 総エントリ数
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                total_entries = cursor.fetchone()[0]

                # 期限切れエントリ数
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at < ?",
                    (datetime.now().isoformat(),),
                )
                expired_entries = cursor.fetchone()[0]

                # データベースサイズ
                cursor = conn.execute(
                    "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
                )
                db_size = cursor.fetchone()[0]

                return {
                    "total_entries": total_entries,
                    "expired_entries": expired_entries,
                    "valid_entries": total_entries - expired_entries,
                    "db_size_bytes": db_size,
                    "db_size_mb": round(db_size / 1024 / 1024, 2),
                }

        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {}

    def get_keys(self, pattern: str = None) -> List[str]:
        """キャッシュキーのリストを取得"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                if pattern:
                    cursor = conn.execute(
                        "SELECT key FROM cache WHERE key LIKE ?", (f"%{pattern}%",)
                    )
                else:
                    cursor = conn.execute("SELECT key FROM cache")

                return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.warning(f"Cache keys error: {e}")
            return []
