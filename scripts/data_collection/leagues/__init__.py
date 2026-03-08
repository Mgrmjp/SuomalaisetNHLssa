"""
League data collection system for prospect tracking.

Supports multiple leagues:
EUROPE:
- Liiga (Finland)
- SHL (Sweden)
- Extraliga (Czech)
- DEL (Germany)
- NL (Switzerland)
- Slovak Extraliga
- ICEHL (Austria/Slovenia)
- KHL (Russia/International)

NORTH AMERICA:
- AHL (Minor pro)
- NCAA (College)
"""

from .base import BaseLeagueAdapter, PlayerStats
from .liiga import LiigaAdapter
from .shl import SHLAdapter
from .ahl import AHLAdapter
from .ncaa import NCAAAdapter
from .del_ import DELAdapter
from .extraliga_cz import CzechExtraligaAdapter
from .nl import SwissNLAdapter
from .icehl import ICEHLAdapter
from .slovak import SlovakExtraligaAdapter
from .khl import KHLAdapter

__all__ = [
    'BaseLeagueAdapter',
    'PlayerStats',
    'LiigaAdapter',
    'SHLAdapter',
    'AHLAdapter',
    'NCAAAdapter',
    'DELAdapter',
    'CzechExtraligaAdapter',
    'SwissNLAdapter',
    'ICEHLAdapter',
    'SlovakExtraligaAdapter',
    'KHLAdapter',
]
