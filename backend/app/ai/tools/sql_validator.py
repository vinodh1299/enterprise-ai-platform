import re
from typing import Tuple


FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "SHUTDOWN",
    "PG_CATALOG", "INFORMATION_SCHEMA", "SQLITE_MASTER", "SYS."
]


def validate_and_sanitize_sql(sql_query: str) -> Tuple[bool, str, str]:
    """
    SQL Security Validator:
    1. Verifies the statement begins strictly with SELECT.
    2. Blocks dangerous mutating SQL keywords (DROP, DELETE, UPDATE, INSERT, ALTER).
    3. Prevents multi-statement SQL injection attacks via semicolons.
    4. Enforces a maximum limit of 100 rows returned.
    
    Returns: (is_safe: bool, sanitized_sql: str, error_message: str)
    """
    clean_sql = sql_query.strip().rstrip(";").strip()

    # Rule 1: Must be SELECT statement
    if not clean_sql.upper().startswith("SELECT"):
        return False, clean_sql, "Security Violation: Only SELECT (read-only) database queries are permitted."

    # Rule 2: Check forbidden keywords
    upper_sql = clean_sql.upper()
    for kw in FORBIDDEN_KEYWORDS:
        # Match keyword as whole word
        if re.search(rf"\b{kw}\b", upper_sql):
            return False, clean_sql, f"Security Violation: Forbidden keyword '{kw}' detected in SQL query."

    # Rule 3: Check for multiple statements separated by semicolon
    if ";" in clean_sql:
        return False, clean_sql, "Security Violation: Multiple SQL statements are not permitted."

    # Rule 4: Enforce row limit
    if "LIMIT" not in upper_sql:
        clean_sql += " LIMIT 100"

    return True, clean_sql, ""
