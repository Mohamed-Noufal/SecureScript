
# This is a dummy python file for testing the security analyzer
import os
import requests

def connect_to_db():
    # Vulnerability 1: Hardcoded secret (Fixing this...)
    api_key = "12345-abcde-67890-fghij"
    
    # Vulnerability 2: SQL Injection (Fixing this...)
    user_input = "admin"
    # The fix should parameterize this query
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    
    return query
