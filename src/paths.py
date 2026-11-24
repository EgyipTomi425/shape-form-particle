"""Repository paths. The simulation CSVs are read from $LFHCAL_DATA (default: the group server's copy)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.environ.get("LFHCAL_DATA", "/home/user/data/simulations")
RESULTS = os.path.join(ROOT, "results")
CACHE = os.path.join(ROOT, "cache")
