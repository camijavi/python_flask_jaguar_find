"""
userModel.py
================================================================================
USER DATA MODEL (PYTHON DATACLASS)
================================================================================
Pure Python data model for User entities across JaguarFind and JaguarMaps.
Adheres strictly to Python standard library dataclasses.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Union


@dataclass
class UserModel:
    """
    UserModel represents a user entity in the JaguarFind system.
    Supports role-specific credential identifiers (CIF, GovermentId, Email)
    as well as both camelCase (userName) and standard username conventions.
    """
    id: Union[str, int]
    username: str = ""
    userName: Optional[str] = None
    email: Optional[str] = None
    fullName: Optional[str] = None
    userTypeId: int = 1
    roleName: str = "Student"
    cif: Optional[str] = None          # 8 digits (Required for Student)
    govermentId: Optional[str] = None  # Required for Collaborator & Visitor
    phoneNumber: Optional[str] = None  # Required for Visitor
    createdAt: Optional[str] = None
    isActive: bool = True

    def __post_init__(self) -> None:
        # Standardize id as string
        self.id = str(self.id)
        # Keep username and userName synchronized
        if not self.userName and self.username:
            self.userName = self.username
        elif not self.username and self.userName:
            self.username = self.userName

    def toDict(self) -> Dict[str, Any]:
        """Serializes UserModel to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "userName": self.userName,
            "email": self.email,
            "fullName": self.fullName,
            "userTypeId": self.userTypeId,
            "roleName": self.roleName,
            "cif": self.cif,
            "govermentId": self.govermentId,
            "phoneNumber": self.phoneNumber,
            "createdAt": self.createdAt,
            "isActive": self.isActive,
        }

    @classmethod
    def fromDict(cls, data: Dict[str, Any]) -> "UserModel":
        """Instantiates UserModel from database row or JSON dictionary."""
        uName = data.get("userName") or data.get("UserName") or data.get("username") or ""
        return cls(
            id=str(data.get("id") or data.get("Id") or ""),
            username=uName,
            userName=uName,
            email=data.get("email") or data.get("Email"),
            fullName=data.get("fullName") or data.get("FullName"),
            userTypeId=int(data.get("userTypeId") or data.get("UserTypeId") or 1),
            roleName=data.get("roleName") or data.get("UserTypeName") or "Student",
            cif=data.get("cif") or data.get("CIF"),
            govermentId=data.get("govermentId") or data.get("GovermentId"),
            phoneNumber=data.get("phoneNumber") or data.get("PhoneNumber"),
            createdAt=data.get("createdAt") or data.get("CreatedAt"),
            isActive=bool(data.get("isActive", data.get("IsActive", True))),
        )
