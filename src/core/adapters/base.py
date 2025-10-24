"""
Base classes and protocols for data adapters
"""

from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.domain.models import Symbol


@runtime_checkable
class SymbolSource(Protocol):
    """銘柄データ取得のプロトコル"""

    def fetch(self) -> List[Symbol]:
        """銘柄リストを取得"""
        ...

    def get_source_name(self) -> str:
        """データソース名を取得"""
        ...

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        ...


class BaseSymbolSource(ABC):
    """銘柄データ取得の基底クラス"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch(self) -> List[Symbol]:
        """銘柄リストを取得"""
        pass

    def get_source_name(self) -> str:
        """データソース名を取得"""
        return self.name

    def is_available(self) -> bool:
        """データソースが利用可能かチェック"""
        return True

    def _normalize_symbol(self, symbol: str) -> str:
        """シンボルの正規化"""
        # NaN や None チェック
        if symbol is None or str(symbol).lower() in ['nan', 'none', '']:
            return ""

        # 一般的な正規化ルール
        symbol = str(symbol).strip().upper()

        # BRK.B → BRK-B, BF.B → BF-B など
        if symbol.endswith(".B"):
            symbol = symbol[:-2] + "-B"
        elif symbol.endswith(".A"):
            symbol = symbol[:-2] + "-A"

        return symbol

    def _validate_symbol(self, symbol: str) -> bool:
        """シンボルのバリデーション"""
        # 空文字列、None、長すぎるシンボルをチェック
        if not symbol or len(symbol) == 0 or len(symbol) > 10:
            return False

        # アルファベットと一部記号のみ許可
        import re

        return bool(re.match(r"^[A-Z0-9\-\.]+$", symbol))


class DataSourceError(Exception):
    """データソースエラー"""

    pass


class NetworkError(DataSourceError):
    """ネットワークエラー"""

    pass


class ParseError(DataSourceError):
    """パースエラー"""

    pass
