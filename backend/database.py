"""
database.py
================================================================================
SQLITE3 RELATIONAL DATABASE & REPOSITORY LAYER FOR JAGUARFIND
================================================================================
Schema and data persistence for Users, Roles, Lost Objects, and Custody States.
Enforces conditional identity constraints (Student CIF, Collaborator/Visitor GovernmentId,
and Admin Email + PasswordHash) with seed prepopulation.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import Config


def getDbConnection(dbPath: Optional[str] = None) -> sqlite3.Connection:
    """
    Returns an active SQLite connection with row_factory=sqlite3.Row
    and foreign key constraints enabled.
    """
    path = dbPath or Config.DATABASE_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ==============================================================================
# SCHEMA DDL DEFINITIONS
# ==============================================================================

DDL_USER_TYPE_TBL = """
CREATE TABLE IF NOT EXISTS UserTypeTbl (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE
);
"""

DDL_USER_TBL = """
CREATE TABLE IF NOT EXISTS UserTbl (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    UserTypeId INTEGER NOT NULL,
    UserName TEXT NULL,
    FullName TEXT NOT NULL,
    CIF TEXT NULL,
    GovermentId TEXT NULL,
    PhoneNumber TEXT NULL,
    Email TEXT NULL,
    PasswordHash TEXT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (UserTypeId) REFERENCES UserTypeTbl(Id) ON DELETE RESTRICT,
    
    CONSTRAINT chk_user_identity CHECK (
        (UserTypeId = 1 AND CIF IS NOT NULL) OR
        (UserTypeId = 2 AND GovermentId IS NOT NULL) OR
        (UserTypeId = 3 AND GovermentId IS NOT NULL AND PhoneNumber IS NOT NULL) OR
        (UserTypeId = 4 AND Email IS NOT NULL AND PasswordHash IS NOT NULL)
    )
);
"""

DDL_USER_INDEXES = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON UserTbl(UserName) WHERE UserName IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_cif ON UserTbl(CIF) WHERE CIF IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_gov_id ON UserTbl(GovermentId) WHERE GovermentId IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON UserTbl(Email) WHERE Email IS NOT NULL;
"""

DDL_LOST_OBJECT_STATE_TBL = """
CREATE TABLE IF NOT EXISTS LostObjectStateTbl (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE
);
"""

DDL_LOST_OBJECT_REPORT_TBL = """
CREATE TABLE IF NOT EXISTS LostObjectReportTbl (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    DateTimeReported DATETIME DEFAULT CURRENT_TIMESTAMP,
    LostObjectStateId INTEGER NOT NULL,
    UserId INTEGER NULL,
    ItemName TEXT NOT NULL,
    Category TEXT NOT NULL DEFAULT 'other',
    Location TEXT NOT NULL,
    Description TEXT NOT NULL,
    SecretDetail TEXT NULL,
    Signature TEXT NULL,
    PhotoUrl TEXT NULL,
    DateTimeResolved DATETIME NULL,
    ResolvedByAdminId INTEGER NULL,
    
    FOREIGN KEY (LostObjectStateId) REFERENCES LostObjectStateTbl(Id),
    FOREIGN KEY (UserId) REFERENCES UserTbl(Id),
    FOREIGN KEY (ResolvedByAdminId) REFERENCES UserTbl(Id)
);
"""


# ==============================================================================
# DATABASE INITIALIZATION & PREPOPULATION (SEEDING)
# ==============================================================================

def initDb(dbPath: Optional[str] = None, seedSampleData: bool = True) -> None:
    """
    Initializes all database tables, constraints, and prepopulates lookup tables
    and sample testing records.
    """
    conn = getDbConnection(dbPath)
    cursor = conn.cursor()

    try:
        # 1. Execute DDL Schema
        cursor.execute(DDL_USER_TYPE_TBL)
        cursor.execute(DDL_USER_TBL)
        # Ensure UserName column exists if table pre-existed
        cursor.execute("PRAGMA table_info(UserTbl);")
        existingCols = [col[1] for col in cursor.fetchall()]
        if "UserName" not in existingCols:
            cursor.execute("ALTER TABLE UserTbl ADD COLUMN UserName TEXT NULL;")

        cursor.executescript(DDL_USER_INDEXES)
        cursor.execute(DDL_LOST_OBJECT_STATE_TBL)
        cursor.execute(DDL_LOST_OBJECT_REPORT_TBL)

        # 2. Prepopulate User Types
        userTypes = [
            (1, "Student"),
            (2, "Collaborator"),
            (3, "Visitor"),
            (4, "Admin")
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO UserTypeTbl (Id, Name) VALUES (?, ?);",
            userTypes
        )

        # 3. Prepopulate Lost Object States
        states = [
            (1, "Reported"),     # Reported online or found on campus
            (2, "In Custody"),   # Safely stored at Building A / CAE
            (3, "Claimed")       # Successfully verified and returned
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO LostObjectStateTbl (Id, Name) VALUES (?, ?);",
            states
        )

        # 4. Optional Seed Sample Data for Testing
        if seedSampleData:
            _seedInitialData(cursor)

        conn.commit()
    finally:
        conn.close()


def _seedInitialData(cursor: sqlite3.Cursor) -> None:
    """Seeds initial demonstration users and lost & found reports."""
    # Seed 1: Admin User (email + password)
    cursor.execute("SELECT Id FROM UserTbl WHERE Email = 'admin@uamv.edu.ni';")
    if not cursor.fetchone():
        adminHash = generate_password_hash("admin123")
        cursor.execute("""
            INSERT INTO UserTbl (UserTypeId, UserName, FullName, Email, PasswordHash)
            VALUES (4, 'admin', 'Administrador CAE Edificio A', 'admin@uamv.edu.ni', ?);
        """, (adminHash,))

    # Seed 2: Student (CIF + FullName)
    cursor.execute("SELECT Id FROM UserTbl WHERE CIF = '22019845';")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO UserTbl (UserTypeId, UserName, FullName, CIF, Email)
            VALUES (1, 'camila.navarro', 'Camila Navarro', '22019845', 'camila.navarro@uamv.edu.ni');
        """)

    # Seed 3: Collaborator (GovernmentId + FullName)
    cursor.execute("SELECT Id FROM UserTbl WHERE GovermentId = '001-150485-0012A';")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO UserTbl (UserTypeId, UserName, FullName, GovermentId, Email)
            VALUES (2, 'roberto.gomez', 'Prof. Roberto Gómez', '001-150485-0012A', 'roberto.gomez@uamv.edu.ni');
        """)

    # Seed 4: Visitor (GovernmentId + PhoneNumber)
    cursor.execute("SELECT Id FROM UserTbl WHERE GovermentId = '001-200392-0045B';")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO UserTbl (UserTypeId, UserName, FullName, GovermentId, PhoneNumber)
            VALUES (3, 'carlos.mendoza', 'Carlos Mendoza', '001-200392-0045B', '+505 8888 1234');
        """)

    # Seed Sample Lost Objects Reports
    cursor.execute("SELECT COUNT(*) AS total FROM LostObjectReportTbl;")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("""
            INSERT INTO LostObjectReportTbl (
                LostObjectStateId, UserId, ItemName, Category, Location,
                Description, SecretDetail
            ) VALUES
            (2, 2, 'Calculadora Casio fx-991LA Plus', 'electronics', 'buildingB',
             'Calculadora científica gris con tapa azul encontrada en aula B-103.',
             'Tiene un sticker pequeño del jaguar en la parte posterior.'),
            (1, 4, 'Termo Yeti Azul Marino', 'personalItems', 'buildingK',
             'Termo de acero inoxidable 26oz olvidado en una mesa exterior de cafetería.',
             'Tiene una abolladura leve en la base inferior.'),
            (3, 2, 'Carnet Universitario UAM', 'documents', 'buildingA',
             'Carnet estudiantil extraviado cerca de las gradas de CAE.',
             'Nombre impreso coincide con matrícula 2026.');
        """)


# ==============================================================================
# REPOSITORY & QUERY HELPERS
# ==============================================================================

def createUser(
    userTypeId: int,
    fullName: str,
    userName: Optional[str] = None,
    cif: Optional[str] = None,
    govermentId: Optional[str] = None,
    phoneNumber: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    dbPath: Optional[str] = None
) -> int:
    """
    Creates a new user adhering to the role-specific credential rules:
    - Student (1): requires cif
    - Collaborator (2): requires govermentId
    - Visitor (3): requires govermentId and phoneNumber
    - Admin (4): requires email and password (automatically hashed)
    """
    passwordHash = generate_password_hash(password) if password else None

    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO UserTbl (
                UserTypeId, UserName, FullName, CIF, GovermentId, PhoneNumber, Email, PasswordHash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (userTypeId, userName.strip() if userName else None, fullName.strip(), cif, govermentId, phoneNumber, email, passwordHash))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def getUserById(userId: int, dbPath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a user by their primary key Id."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, ut.Name AS UserTypeName
            FROM UserTbl u
            JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id
            WHERE u.Id = ?;
        """, (userId,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def getUserByIdentifier(
    identifier: str,
    userTypeId: Optional[int] = None,
    dbPath: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Resolves a user by their specific role identifier:
    - If userTypeId=1: checks CIF
    - If userTypeId IN (2, 3): checks GovermentId
    - If userTypeId=4: checks Email
    - If userTypeId is None: searches across CIF, GovermentId, and Email
    """
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cleanId = identifier.strip()

        if userTypeId == 1:
            query = "SELECT u.*, ut.Name AS UserTypeName FROM UserTbl u JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id WHERE u.CIF = ?;"
            cursor.execute(query, (cleanId,))
        elif userTypeId in (2, 3):
            query = "SELECT u.*, ut.Name AS UserTypeName FROM UserTbl u JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id WHERE u.GovermentId = ?;"
            cursor.execute(query, (cleanId,))
        elif userTypeId == 4:
            query = "SELECT u.*, ut.Name AS UserTypeName FROM UserTbl u JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id WHERE u.Email = ?;"
            cursor.execute(query, (cleanId.lower(),))
        else:
            query = """
                SELECT u.*, ut.Name AS UserTypeName
                FROM UserTbl u
                JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id
                WHERE u.CIF = ? OR u.GovermentId = ? OR u.Email = ? OR u.UserName = ?;
            """
            cursor.execute(query, (cleanId, cleanId, cleanId.lower(), cleanId))

        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def getUserByUsername(userName: str, dbPath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a user by their unique UserName handle."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, ut.Name AS UserTypeName
            FROM UserTbl u
            JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id
            WHERE LOWER(u.UserName) = LOWER(?);
        """, (userName.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def authenticateAdmin(email: str, password: str, dbPath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Validates admin credentials using email and secure password hashing."""
    user = getUserByIdentifier(email, userTypeId=4, dbPath=dbPath)
    if not user:
        return None
    if user["PasswordHash"] and check_password_hash(user["PasswordHash"], password):
        return user
    return None


def createLostObjectReport(
    itemName: str,
    location: str,
    description: str,
    category: str = "other",
    userId: Optional[int] = None,
    lostObjectStateId: int = 1,
    secretDetail: Optional[str] = None,
    signature: Optional[str] = None,
    photoUrl: Optional[str] = None,
    dbPath: Optional[str] = None
) -> int:
    """Creates a new lost & found object report."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO LostObjectReportTbl (
                ItemName, Category, Location, Description, UserId,
                LostObjectStateId, SecretDetail, Signature, PhotoUrl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (itemName.strip(), category, location.strip(), description.strip(),
              userId, lostObjectStateId, secretDetail, signature, photoUrl))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def getAllLostObjects(
    stateId: Optional[int] = None,
    category: Optional[str] = None,
    dbPath: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves all lost & found items with optional filtering by state or category."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        query = """
            SELECT r.*, s.Name AS StateName, u.FullName AS ReporterName
            FROM LostObjectReportTbl r
            JOIN LostObjectStateTbl s ON r.LostObjectStateId = s.Id
            LEFT JOIN UserTbl u ON r.UserId = u.Id
            WHERE 1=1
        """
        params = []
        if stateId:
            query += " AND r.LostObjectStateId = ?"
            params.append(stateId)
        if category:
            query += " AND r.Category = ?"
            params.append(category)

        query += " ORDER BY r.DateTimeReported DESC;"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def getLostObjectById(reportId: int, dbPath: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single lost object report with full state and user details."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.*, s.Name AS StateName, u.FullName AS ReporterName
            FROM LostObjectReportTbl r
            JOIN LostObjectStateTbl s ON r.LostObjectStateId = s.Id
            LEFT JOIN UserTbl u ON r.UserId = u.Id
            WHERE r.Id = ?;
        """, (reportId,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def updateLostObjectState(
    reportId: int,
    newStateId: int,
    resolvedByAdminId: Optional[int] = None,
    dbPath: Optional[str] = None
) -> bool:
    """Updates custody status of an item (e.g. from Reported to In Custody or Claimed)."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        if newStateId == 3:  # Claimed / Delivered
            cursor.execute("""
                UPDATE LostObjectReportTbl
                SET LostObjectStateId = ?,
                    DateTimeResolved = CURRENT_TIMESTAMP,
                    ResolvedByAdminId = ?
                WHERE Id = ?;
            """, (newStateId, resolvedByAdminId, reportId))
        else:
            cursor.execute("""
                UPDATE LostObjectReportTbl
                SET LostObjectStateId = ?
                WHERE Id = ?;
            """, (newStateId, reportId))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def getAllUsers(dbPath: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all registered users without sensitive password hashes."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.Id, u.UserTypeId, ut.Name AS UserTypeName, u.UserName,
                   u.FullName, u.CIF, u.GovermentId, u.PhoneNumber, u.Email,
                   u.CreatedAt, u.IsActive
            FROM UserTbl u
            JOIN UserTypeTbl ut ON u.UserTypeId = ut.Id
            ORDER BY u.Id ASC;
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def getCustodyStates(dbPath: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves lookup table of custody states."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Name FROM LostObjectStateTbl ORDER BY Id ASC;")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def getSystemStats(dbPath: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves system-wide summary metrics for reports and users."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM LostObjectReportTbl;")
        totalItems = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM LostObjectReportTbl WHERE LostObjectStateId = 1;")
        reportedItems = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM LostObjectReportTbl WHERE LostObjectStateId = 2;")
        inCustodyItems = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM LostObjectReportTbl WHERE LostObjectStateId = 3;")
        claimedItems = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM UserTbl;")
        totalUsers = cursor.fetchone()[0]

        return {
            "totalItems": totalItems,
            "reportedItems": reportedItems,
            "inCustodyItems": inCustodyItems,
            "claimedItems": claimedItems,
            "totalUsers": totalUsers,
        }
    finally:
        conn.close()


def updateUserPassword(userId: int, newPassword: str, dbPath: Optional[str] = None) -> bool:
    """Updates a user's password with secure Werkzeug hashing."""
    passwordHash = generate_password_hash(newPassword)
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE UserTbl SET PasswordHash = ? WHERE Id = ?;", (passwordHash, userId))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def updateUserStatus(userId: int, isActive: bool, dbPath: Optional[str] = None) -> bool:
    """Toggles active status (active or deactivated / dada de baja) for a user account."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE UserTbl SET IsActive = ? WHERE Id = ?;", (1 if isActive else 0, userId))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def updateUserRole(
    userId: int,
    newUserTypeId: int,
    cif: Optional[str] = None,
    govermentId: Optional[str] = None,
    phoneNumber: Optional[str] = None,
    dbPath: Optional[str] = None
) -> bool:
    """Updates the role (UserTypeId) assigned to a user, ensuring identity constraints hold."""
    conn = getDbConnection(dbPath)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UserTbl WHERE Id = ?;", (userId,))
        curr = dict(cursor.fetchone() or {})
        effCif = cif or curr.get("CIF")
        effGov = govermentId or curr.get("GovermentId")
        effPhone = phoneNumber or curr.get("PhoneNumber")
        # If transitioning to Collaborator or Visitor without GovId, provide fallback or preserve
        if newUserTypeId in (2, 3) and not effGov:
            effGov = curr.get("CIF") or "000-000000-0000X"
        if newUserTypeId == 3 and not effPhone:
            effPhone = "+505 0000 0000"
        cursor.execute("""
            UPDATE UserTbl
            SET UserTypeId = ?, CIF = ?, GovermentId = ?, PhoneNumber = ?
            WHERE Id = ?;
        """, (newUserTypeId, effCif, effGov, effPhone, userId))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
