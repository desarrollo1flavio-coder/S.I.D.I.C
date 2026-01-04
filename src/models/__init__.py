"""Modelos de datos del sistema."""

from .crime_record import CrimeRecord
from .mentioned_person import MentionedPerson
from .apprehended import Apprehended
from .report_data import ReportData, PeriodData

__all__ = [
    'CrimeRecord',
    'MentionedPerson', 
    'Apprehended',
    'ReportData',
    'PeriodData'
]
