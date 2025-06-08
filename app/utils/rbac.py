# ds-rpc-01/app/utils/rbac.py

from pathlib import Path

# Define the base path to your data resources
RESOURCES_PATH = Path(__file__).parent.parent.parent / "resources" / "data"

# Map roles to the data directories they are allowed to access.
# C-Level has access to all directories.
ROLE_PERMISSIONS = {
    "finance": [RESOURCES_PATH / "finance"],
    "marketing": [RESOURCES_PATH / "marketing"],
    "hr": [RESOURCES_PATH / "hr"],
    "engineering": [RESOURCES_PATH / "engineering"],
    "employee": [RESOURCES_PATH / "general"],
    "c-level": [
        RESOURCES_PATH / "finance",
        RESOURCES_PATH / "marketing",
        RESOURCES_PATH / "hr",
        RESOURCES_PATH / "engineering",
        RESOURCES_PATH / "general",
    ],
}

def get_accessible_files(role: str):
    """
    Retrieves a list of all file paths a given role has access to.
    """
    accessible_files = []
    if role in ROLE_PERMISSIONS:
        for path in ROLE_PERMISSIONS[role]:
            if path.is_dir():
                # Add all files in the directory
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        accessible_files.append(str(file_path))
    return accessible_files
