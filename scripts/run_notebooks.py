"""Execute notebooks in place (outputs saved even if a cell fails), in the given order; one log line per notebook.
    python scripts/run_notebooks.py report_notebooks/01_gflash_electron.ipynb ...     (the kernel starts in the notebook's folder)"""
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

for path in sys.argv[1:]:
    t0 = time.time()
    nb = nbformat.read(path, as_version=4)
    folder = path.rsplit("/", 1)[0] if "/" in path else "."
    status = "ok"
    try:
        NotebookClient(nb, timeout=14400, kernel_name="python3", resources={"metadata": {"path": folder}}).execute()
    except CellExecutionError as e:
        status = f"ERROR {str(e).splitlines()[-1][:200] if str(e) else ''}"
    nbformat.write(nb, path)
    print(f"{path}: {status} after {time.time() - t0:.0f} s", flush=True)
