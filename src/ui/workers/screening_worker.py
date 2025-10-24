"""
スクリーニングワーカー - 非同期処理用
"""

import logging

from PySide6.QtCore import QObject, QThread, Signal

try:
    from ...core.application.screening_service import ScreeningService
    from ...core.domain.models import Rule40Result, ScreeningConfig
except ImportError:
    try:
        from src.core.application.screening_service import ScreeningService
        from src.core.domain.models import Rule40Result, ScreeningConfig
    except ImportError:
        # Fallback for direct execution
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        from src.core.application.screening_service import ScreeningService
        from src.core.domain.models import Rule40Result, ScreeningConfig

logger = logging.getLogger(__name__)


class ScreeningWorker(QObject):
    """スクリーニング処理ワーカー"""

    # シグナル
    progress_updated = Signal(int, int, str)  # current, total, message
    result_found = Signal(Rule40Result)  # 個別結果
    finished = Signal(list)  # 全結果
    error = Signal(str)  # エラー
    status_updated = Signal(str)  # ステータス更新

    def __init__(self, config: ScreeningConfig, config_manager):
        super().__init__()
        self.config = config
        self.config_manager = config_manager
        self._is_running = False
        self.service = None

    def start_screening(self):
        """スクリーニング開始"""
        try:
            self._is_running = True
            self.status_updated.emit("スクリーニングサービスを初期化中...")

            # サービス作成
            self.service = ScreeningService(self.config_manager)

            # プログレスコールバック設定
            def progress_callback(current: int, total: int, message: str):
                if self._is_running:
                    self.progress_updated.emit(current, total, message)

            def result_callback(result: Rule40Result):
                if self._is_running:
                    self.result_found.emit(result)

            self.status_updated.emit("銘柄データを取得中...")

            # スクリーニング実行
            results = self.service.screen_stocks(
                self.config,
                progress_callback=progress_callback,
                result_callback=result_callback,
            )

            if self._is_running:
                self.status_updated.emit(f"スクリーニング完了: {len(results)}件")
                self.finished.emit(results)
            else:
                self.status_updated.emit("スクリーニングが中断されました")

        except Exception as e:
            logger.error(f"Screening error: {e}")
            self.error.emit(f"スクリーニングエラー: {str(e)}")
        finally:
            self._is_running = False

    def stop_screening(self):
        """スクリーニング停止"""
        self._is_running = False
        self.status_updated.emit("スクリーニングを停止中...")


class ScreeningThread(QThread):
    """スクリーニングスレッド"""

    def __init__(self, worker: ScreeningWorker):
        super().__init__()
        self.worker = worker

    def run(self):
        """スレッド実行"""
        self.worker.start_screening()

    def stop(self):
        """スレッド停止"""
        self.worker.stop_screening()
        self.quit()
        self.wait()
