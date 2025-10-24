"""
Rule of 40 計算エンジン
"""

import logging
from datetime import datetime
from typing import Optional, Protocol

try:
    from .models import (
        CalculationError,
        CalculationPeriod,
        DataQuality,
        FinancialData,
        Rule40Result,
        Rule40Variant,
    )
except ImportError:
    from src.core.domain.models import (
        CalculationError,
        CalculationPeriod,
        DataQuality,
        FinancialData,
        Rule40Result,
        Rule40Variant,
    )


logger = logging.getLogger(__name__)


class Rule40Strategy(Protocol):
    """Rule of 40 計算戦略"""

    def calculate(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]: ...


class OPStrategy:
    """営業利益版 Rule of 40 計算戦略"""

    def calculate(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """営業利益版の Rule of 40 を計算"""
        try:
            # 売上成長率計算
            rev_growth = self._calculate_revenue_growth(data, period)
            if rev_growth is None:
                return None

            # 営業利益率計算
            op_margin = self._calculate_operating_margin(data, period)
            if op_margin is None:
                return None

            # Rule of 40 = 売上成長率(%) + 営業利益率(%)
            r40 = rev_growth * 100 + op_margin * 100
            return r40

        except Exception as e:
            logger.warning(f"Error in OP strategy calculation: {e}")
            return None

    def _calculate_revenue_growth(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """売上成長率を計算"""
        try:
            if period == CalculationPeriod.TTM:
                # infoから成長率を取得
                if data.info and "revenueGrowth" in data.info:
                    return data.info["revenueGrowth"]
                
                # TTMデータから計算
                if (
                    data.revenue_ttm is not None
                    and hasattr(data.revenue_ttm, 'iloc')
                    and len(data.revenue_ttm) > 1
                ):
                    current = data.revenue_ttm.iloc[0]
                    previous = data.revenue_ttm.iloc[1]
                    if previous != 0:
                        return (current / previous) - 1

            elif period == CalculationPeriod.ANNUAL:
                # 年次データから計算
                if (
                    data.revenue_annual is not None
                    and hasattr(data.revenue_annual, 'iloc')
                    and len(data.revenue_annual) > 1
                ):
                    current = data.revenue_annual.iloc[0]
                    previous = data.revenue_annual.iloc[1]
                    if previous != 0:
                        return (current / previous) - 1

            return None

        except Exception as e:
            logger.warning(f"Error calculating revenue growth: {e}")
            return None

        except Exception as e:
            logger.warning(f"Error calculating revenue growth: {e}")
            return None

    def _calculate_operating_margin(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """営業利益率を計算"""
        try:
            if period == CalculationPeriod.TTM:
                # infoからマージンを取得
                if data.info and "operatingMargins" in data.info:
                    return data.info["operatingMargins"]
                
                # TTMデータから計算
                if (
                    data.operating_income_ttm is not None
                    and data.revenue_ttm is not None
                    and hasattr(data.operating_income_ttm, 'iloc')
                    and hasattr(data.revenue_ttm, 'iloc')
                    and len(data.operating_income_ttm) > 0
                    and len(data.revenue_ttm) > 0
                ):
                    op_income = data.operating_income_ttm.iloc[0]
                    revenue = data.revenue_ttm.iloc[0]
                    if revenue != 0:
                        return op_income / revenue

            elif period == CalculationPeriod.ANNUAL:
                # 年次データから計算
                if (
                    data.operating_income_annual is not None
                    and data.revenue_annual is not None
                    and hasattr(data.operating_income_annual, 'iloc')
                    and hasattr(data.revenue_annual, 'iloc')
                    and len(data.operating_income_annual) > 0
                    and len(data.revenue_annual) > 0
                ):
                    op_income = data.operating_income_annual.iloc[0]
                    revenue = data.revenue_annual.iloc[0]
                    if revenue != 0:
                        return op_income / revenue

            return None

        except Exception as e:
            logger.warning(f"Error calculating operating margin: {e}")
            return None


class EBITDAStrategy:
    """EBITDA版 Rule of 40 計算戦略"""

    def calculate(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """EBITDA版の Rule of 40 を計算"""
        try:
            # 売上成長率計算
            rev_growth = self._calculate_revenue_growth(data, period)
            if rev_growth is None:
                return None

            # EBITDAマージン計算
            ebitda_margin = self._calculate_ebitda_margin(data, period)
            if ebitda_margin is None:
                return None

            # Rule of 40 = 売上成長率(%) + EBITDAマージン(%)
            r40 = rev_growth * 100 + ebitda_margin * 100
            return r40

        except Exception as e:
            logger.warning(f"Error in EBITDA strategy calculation: {e}")
            return None

    def _calculate_revenue_growth(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """売上成長率を計算"""
        # OPStrategy と同じロジック
        op_strategy = OPStrategy()
        return op_strategy._calculate_revenue_growth(data, period)

    def _calculate_ebitda_margin(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """EBITDAマージンを計算"""
        try:
            if period == CalculationPeriod.TTM:
                if (
                    data.operating_income_ttm is not None
                    and data.revenue_ttm is not None
                    and data.depreciation_ttm is not None
                    and len(data.operating_income_ttm) > 0
                    and len(data.revenue_ttm) > 0
                    and len(data.depreciation_ttm) > 0
                ):

                    op_income = data.operating_income_ttm.iloc[0]
                    depreciation = data.depreciation_ttm.iloc[0]
                    revenue = data.revenue_ttm.iloc[0]

                    if revenue != 0:
                        ebitda = op_income + depreciation
                        return ebitda / revenue

            elif period == CalculationPeriod.ANNUAL:
                if (
                    data.operating_income_annual is not None
                    and data.revenue_annual is not None
                    and data.depreciation_annual is not None
                    and len(data.operating_income_annual) > 0
                    and len(data.revenue_annual) > 0
                    and len(data.depreciation_annual) > 0
                ):

                    op_income = data.operating_income_annual.iloc[0]
                    depreciation = data.depreciation_annual.iloc[0]
                    revenue = data.revenue_annual.iloc[0]

                    if revenue != 0:
                        ebitda = op_income + depreciation
                        return ebitda / revenue

            return None

        except Exception as e:
            logger.warning(f"Error calculating EBITDA margin: {e}")
            return None


class Rule40Calculator:
    """Rule of 40 計算クラス"""

    def __init__(self):
        self.op_strategy = OPStrategy()
        self.ebitda_strategy = EBITDAStrategy()

    def calculate(
        self,
        data: FinancialData,
        period: CalculationPeriod = CalculationPeriod.TTM,
        variant: Rule40Variant = Rule40Variant.OP,
    ) -> Rule40Result:
        """Rule of 40 を計算"""
        try:
            logger.debug(
                f"Calculating Rule of 40 for {data.symbol}, period: {period}, variant: {variant}"
            )

            result = Rule40Result(
                symbol=data.symbol,
                period=period,
                variant=variant,
                calculation_time=datetime.now(),
            )

            # 売上成長率計算（共通）
            result.revenue_growth_yoy = self._calculate_revenue_growth(data, period)

            # 営業利益率計算
            result.operating_margin = self._calculate_operating_margin(data, period)

            # EBITDAマージン計算
            result.ebitda_margin = self._calculate_ebitda_margin(data, period)

            # バリアントに応じて R40 を計算
            if variant in [Rule40Variant.OP, Rule40Variant.BOTH]:
                result.r40_op = self.op_strategy.calculate(data, period)

            if variant in [Rule40Variant.EBITDA, Rule40Variant.BOTH]:
                result.r40_ebitda = self.ebitda_strategy.calculate(data, period)

            # データ品質を評価
            result.data_quality = self._evaluate_result_quality(result)

            logger.debug(
                f"Calculation completed for {data.symbol}: {result.data_quality}"
            )
            return result

        except Exception as e:
            logger.error(f"Error calculating Rule of 40 for {data.symbol}: {e}")
            raise CalculationError(
                f"Failed to calculate Rule of 40 for {data.symbol}: {e}"
            )

    def _calculate_revenue_growth(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """売上成長率を計算"""
        return self.op_strategy._calculate_revenue_growth(data, period)

    def _calculate_operating_margin(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """営業利益率を計算"""
        return self.op_strategy._calculate_operating_margin(data, period)

    def _calculate_ebitda_margin(
        self, data: FinancialData, period: CalculationPeriod
    ) -> Optional[float]:
        """EBITDAマージンを計算"""
        return self.ebitda_strategy._calculate_ebitda_margin(data, period)

    def _evaluate_result_quality(self, result: Rule40Result) -> DataQuality:
        """計算結果の品質を評価"""
        has_revenue_growth = result.revenue_growth_yoy is not None
        has_op_margin = result.operating_margin is not None
        has_ebitda_margin = result.ebitda_margin is not None
        has_r40_op = result.r40_op is not None
        has_r40_ebitda = result.r40_ebitda is not None

        if (
            has_revenue_growth
            and (has_op_margin or has_ebitda_margin)
            and (has_r40_op or has_r40_ebitda)
        ):
            return DataQuality.COMPLETE
        elif has_revenue_growth or has_op_margin or has_ebitda_margin:
            return DataQuality.PARTIAL
        else:
            return DataQuality.MISSING
