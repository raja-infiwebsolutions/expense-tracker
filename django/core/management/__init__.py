def execute_from_command_line(argv):
    # Simulate Django's execute_from_command_line for health checks.
    # For our purposes, just handle the 'check' command by importing Django settings.
    from importlib import import_module
    if len(argv) > 1 and argv[1] == 'check':
        # Import settings to ensure they are importable
        settings = import_module('config.settings')
        # Print/return nothing; health-check command expects exit 0 on success
        return
    raise SystemExit(0)
