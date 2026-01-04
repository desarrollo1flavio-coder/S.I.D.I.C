"""
Widgets personalizados para la UI de S.I.D.I.C.
"""
from .file_selector import ShapefileSelector
from .period_selector import PeriodSelector, ComparativePeriodSelector

__all__ = [
    'ShapefileSelector',
    'PeriodSelector',
    'ComparativePeriodSelector'
]
