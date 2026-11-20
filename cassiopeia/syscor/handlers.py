import logging

from django.db import transaction


# Stores Python log records in the application database.
# Ukládá záznamy protokolu Pythonu do databáze aplikace.
class DatabaseLogHandler(logging.Handler):
    # Saves a formatted log message and its source location.
    # Ukládá formátovanou zprávu protokolu a její umístění ve zdrojovém kódu.
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