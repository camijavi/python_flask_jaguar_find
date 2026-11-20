"""
lostFoundObjectModel.py
================================================================================
LOST & FOUND OBJECT DATA MODEL (PYTHON DATACLASS)
================================================================================
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LostFoundObjectModel:
    id: int
    itemName: str
    category: str
    location: str
    description: str
    lostObjectStateId: int = 1         # 1: Reported, 2: In Custody, 3: Claimed
    stateName: str = "Reported"
    badgeColor: str = "amber"
    secretDetail: Optional[str] = None # Anti-fraud hidden detail (admin only)
    hasSecretDetail: bool = False
    hasSignature: bool = False
    signature: Optional[str] = None
    photoUrl: Optional[str] = None
    userId: Optional[int] = None
    reporterName: Optional[str] = None
    dateTimeReported: Optional[str] = None
    dateTimeResolved: Optional[str] = None
    resolvedByAdminId: Optional[int] = None
