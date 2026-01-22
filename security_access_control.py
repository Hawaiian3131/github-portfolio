"""
Access Control & Permissions Module
User authentication, role-based access control (RBAC), audit trail
"""
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Role(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    USER = "user"
    READ_ONLY = "read_only"


class Permission(Enum):
    """Granular permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ORGANIZE = "organize"
    ENCRYPT = "encrypt"
    SCHEDULE = "schedule"
    CONFIG = "config"
    AUDIT = "audit"


# Role permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    Role.USER: [Permission.READ, Permission.WRITE, Permission.ORGANIZE, Permission.SCHEDULE],
    Role.READ_ONLY: [Permission.READ]
}


class User:
    def __init__(self, username: str, password_hash: str, role: Role, email: str = None):
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.email = email
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        self.failed_attempts = 0
        self.locked = False
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role.value,
            "email": self.email,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "failed_attempts": self.failed_attempts,
            "locked": self.locked
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'User':
        user = User(
            data["username"],
            data["password_hash"],
            Role(data["role"]),
            data.get("email")
        )
        user.created_at = data["created_at"]
        user.last_login = data.get("last_login")
        user.failed_attempts = data.get("failed_attempts", 0)
        user.locked = data.get("locked", False)
        return user


class AccessControl:
    def __init__(self, users_file: Path = None):
        """
        Initialize access control system
        
        Args:
            users_file: Path to users database JSON file
        """
        self.users_file = users_file or Path("users.json")
        self.audit_file = Path("audit_trail.json")
        self.users: Dict[str, User] = {}
        self.current_user: Optional[User] = None
        self.load_users()
    
    def load_users(self):
        """Load users from database"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                self.users = {
                    username: User.from_dict(user_data)
                    for username, user_data in data.items()
                }
    
    def save_users(self):
        """Save users to database"""
        with open(self.users_file, 'w') as f:
            data = {
                username: user.to_dict()
                for username, user in self.users.items()
            }
            json.dump(data, f, indent=4)
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + pwdhash.hex()
    
    def verify_password(self, stored_hash: str, password: str) -> bool:
        """Verify password against hash"""
        salt = stored_hash[:64]
        stored_pwdhash = stored_hash[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwdhash.hex() == stored_pwdhash
    
    def create_user(self, username: str, password: str, role: Role, email: str = None) -> Tuple[bool, str]:
        """
        Create new user
        
        Args:
            username: Username
            password: Plain text password
            role: User role
            email: Optional email
            
        Returns:
            (success, message)
        """
        # Check permission
        if not self.has_permission(Permission.CONFIG):
            return False, "Permission denied: CONFIG permission required"
        
        if username in self.users:
            return False, f"User '{username}' already exists"
        
        password_hash = self.hash_password(password)
        user = User(username, password_hash, role, email)
        self.users[username] = user
        self.save_users()
        
        self.log_event("USER_CREATE", f"Created user: {username} with role: {role.value}")
        return True, f"User '{username}' created successfully"
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user
        
        Args:
            username: Username
            password: Password
            
        Returns:
            (success, message)
        """
        if username not in self.users:
            self.log_event("AUTH_FAIL", f"Login attempt for non-existent user: {username}")
            return False, "Invalid username or password"
        
        user = self.users[username]
        
        # Check if locked
        if user.locked:
            self.log_event("AUTH_FAIL", f"Login attempt for locked user: {username}")
            return False, "Account is locked. Contact administrator."
        
        # Verify password
        if self.verify_password(user.password_hash, password):
            user.last_login = datetime.now().isoformat()
            user.failed_attempts = 0
            self.current_user = user
            self.save_users()
            self.log_event("AUTH_SUCCESS", f"User logged in: {username}")
            return True, "Authentication successful"
        else:
            user.failed_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_attempts >= 5:
                user.locked = True
                self.log_event("ACCOUNT_LOCK", f"Account locked due to failed attempts: {username}")
            
            self.save_users()
            self.log_event("AUTH_FAIL", f"Failed login attempt for user: {username}")
            return False, "Invalid username or password"
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            self.log_event("LOGOUT", f"User logged out: {self.current_user.username}")
            self.current_user = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if current user has permission"""
        if not self.current_user:
            return False
        
        return permission in ROLE_PERMISSIONS[self.current_user.role]
    
    def require_permission(self, permission: Permission) -> Tuple[bool, str]:
        """
        Require permission for operation
        
        Returns:
            (authorized, message)
        """
        if not self.current_user:
            return False, "Not authenticated"
        
        if self.has_permission(permission):
            return True, "Authorized"
        else:
            self.log_event("AUTH_FAIL", f"Permission denied: {permission.value} for user: {self.current_user.username}")
            return False, f"Permission denied: {permission.value} permission required"
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change current user's password"""
        if not self.current_user:
            return False, "Not authenticated"
        
        if not self.verify_password(self.current_user.password_hash, old_password):
            return False, "Incorrect current password"
        
        self.current_user.password_hash = self.hash_password(new_password)
        self.save_users()
        self.log_event("PASSWORD_CHANGE", f"Password changed for user: {self.current_user.username}")
        return True, "Password changed successfully"
    
    def reset_failed_attempts(self, username: str) -> Tuple[bool, str]:
        """Reset failed login attempts (admin only)"""
        if not self.has_permission(Permission.CONFIG):
            return False, "Permission denied"
        
        if username not in self.users:
            return False, f"User '{username}' not found"
        
        user = self.users[username]
        user.failed_attempts = 0
        user.locked = False
        self.save_users()
        self.log_event("ACCOUNT_UNLOCK", f"Account unlocked: {username}")
        return True, f"User '{username}' unlocked"
    
    def log_event(self, event_type: str, description: str, severity: str = "INFO"):
        """
        Log security event to audit trail
        
        Args:
            event_type: Type of event
            description: Event description
            severity: INFO, WARNING, CRITICAL
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": self.current_user.username if self.current_user else "SYSTEM",
            "description": description,
            "severity": severity
        }
        
        # Append to audit log
        try:
            if self.audit_file.exists():
                with open(self.audit_file, 'r') as f:
                    audit_log = json.load(f)
            else:
                audit_log = []
            
            audit_log.append(event)
            
            with open(self.audit_file, 'w') as f:
                json.dump(audit_log, f, indent=4)
        except Exception as e:
            print(f"Failed to log event: {e}")
    
    def get_audit_trail(self, user: str = None, event_type: str = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve audit trail
        
        Args:
            user: Filter by username
            event_type: Filter by event type
            limit: Maximum records to return
            
        Returns:
            List of audit events
        """
        if not self.has_permission(Permission.AUDIT):
            return []
        
        try:
            with open(self.audit_file, 'r') as f:
                audit_log = json.load(f)
            
            # Apply filters
            if user:
                audit_log = [e for e in audit_log if e['user'] == user]
            if event_type:
                audit_log = [e for e in audit_log if e['event_type'] == event_type]
            
            # Return most recent first
            return list(reversed(audit_log))[:limit]
        except:
            return []
    
    def get_user_list(self) -> List[Dict]:
        """Get list of all users (admin only)"""
        if not self.has_permission(Permission.CONFIG):
            return []
        
        return [
            {
                "username": user.username,
                "role": user.role.value,
                "email": user.email,
                "last_login": user.last_login,
                "locked": user.locked
            }
            for user in self.users.values()
        ]


# Default admin account (change password on first login!)
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "ChangeMe123!",  # CHANGE THIS
    "role": Role.ADMIN,
    "email": "admin@fileorganizer.local"
}
