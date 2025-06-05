from pathlib import Path

def get_role_data_path(role: str, base_path: Path) -> Path:
    """
    Returns the folder path for the given user role.
    Falls back to 'general' if the role is not found.
    """
    role_map = {
        "finance": "finance",
        "marketing": "marketing",
        "hr": "hr",
        "engineering": "engineering",
        "general": "general"
    }
    folder = role_map.get(role.lower(), "general")
    return base_path / folder
