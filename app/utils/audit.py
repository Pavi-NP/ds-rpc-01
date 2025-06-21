# ds-rpc-02/app/utils/audit.py

import os
import logging

# Ensure the logs directory exists
logs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(logs_dir, exist_ok=True)

# Set the log file path
log_file_path = os.path.join(logs_dir, "audit.log")

# Configure the logger
audit_logger = logging.getLogger("audit_logger")
audit_logger.setLevel(logging.INFO)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_file_path)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
audit_logger.addHandler(console_handler)
audit_logger.addHandler(file_handler)

# Define logging functions
def log_authentication_success(username: str, role: str):
    audit_logger.info(f"Authentication success: User '{username}' with role '{role}'.")

def log_authentication_failure(username: str, reason: str):
    audit_logger.warning(f"Authentication failure: User '{username}', Reason: {reason}")

def log_query(username: str, query: str, query_id: str, user_role: str):
    audit_logger.info(f"Query {query_id} from user '{username}': {query}")

def log_query_success(username: str, query_id: str, processing_time_ms: int, sources_count: int):
    audit_logger.info(f"Query {query_id} from '{username}' succeeded in {processing_time_ms} ms with {sources_count} sources.")

def log_query_error(username: str, query_id: str, error: str):
    audit_logger.error(f"Query {query_id} from '{username}' failed: {error}")
    