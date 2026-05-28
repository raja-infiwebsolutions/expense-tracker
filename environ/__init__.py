import os
from pathlib import Path

class Env:
    def __init__(self, **kwargs):
        # store defaults types if provided, but not strictly needed for health check
        self.vars = kwargs

    @classmethod
    def read_env(cls, path):
        try:
            p = Path(path)
            if not p.exists():
                return
            with p.open() as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key, val)
        except Exception:
            return

    def __call__(self, key, default=None):
        val = os.environ.get(key, None)
        if val is None:
            return default
        # try to infer booleans
        low = val.lower()
        if low in ('true', '1', 'yes', 'on'):
            return True
        if low in ('false', '0', 'no', 'off'):
            return False
        return val

    def list(self, key, default=None):
        if default is None:
            default = []
        val = os.environ.get(key, None)
        if val is None or val == '':
            return default
        return [p.strip() for p in val.split(',') if p.strip()]

    def db(self, key, default=None):
        return os.environ.get(key, default)

# Provide a module-level Env for convenience
Env = Env

def __getattr__(name):
    # allow 'Env' attribute to be imported
    if name == 'Env':
        return Env
    raise AttributeError(name)
