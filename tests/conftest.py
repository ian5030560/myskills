"""
Pytest configuration and fixtures for write-paper-notes tests
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "write-paper-notes" / "scripts"))
