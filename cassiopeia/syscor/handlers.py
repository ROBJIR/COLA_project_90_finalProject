import logging

from django.db import transaction


class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        from syscor.models import PythonLog

        try:
            with transaction.atomic():
                PythonLog.objects.create(
                    level=record.levelname,
                    logger_name=record.name,
                    message=self.format(record),
                    pathname=record.pathname,
                    lineno=record.lineno,
                    func_name=record.funcName,
                )
        except Exception:
            self.handleError(record)