import glob
import os


def worker_exit(server, worker):
    clean_metrics_files(worker.pid)


def clean_metrics_files(pid):
    """Do bookkeeping for when one process dies in a multi-process setup."""
    path = os.environ.get("PROMETHEUS_MULTIPROC_DIR", os.environ.get("prometheus_multiproc_dir"))
    for f in glob.glob(os.path.join(path, f"counter_{pid}.db")):
        os.remove(f)
    for f in glob.glob(os.path.join(path, f"gauge_all_{pid}.db")):
        os.remove(f)
    for f in glob.glob(os.path.join(path, f"histogram_{pid}.db")):
        os.remove(f)
