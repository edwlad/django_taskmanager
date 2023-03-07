#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

    # если найдены настройки для запуска Coverage
    cov_run = False
    cov_show_missing = False
    cov_skip_covered = False
    cov_skip_empty = False
    if "--cov" in sys.argv:
        from coverage import Coverage

        sys.argv.remove("--cov")
        cov_run = True
        cov_main = Coverage()
        cov_main.erase()
        cov_main.set_option("run:source", ("app_task", "api_task"))
        cov_main.start()
    if "--show-missing" in sys.argv:
        sys.argv.remove("--show-missing")
        cov_show_missing = True
    if "--skip-covered" in sys.argv:
        sys.argv.remove("--skip-covered")
        cov_skip_covered = True
    if "--skip-empty" in sys.argv:
        sys.argv.remove("--skip-empty")
        cov_skip_empty = True

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    # если запущен Coverage
    if cov_run:
        cov_main.stop()
        cov_main.report(
            show_missing=cov_show_missing,
            skip_covered=cov_skip_covered,
            skip_empty=cov_skip_empty,
        )


if __name__ == "__main__":
    main()
