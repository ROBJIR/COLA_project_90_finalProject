from django.db import models

class PythonLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=10, db_index=True)
    logger_name = models.CharField(max_length=255)
    message = models.TextField()
    pathname = models.TextField()
    lineno = models.PositiveIntegerField()
    func_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["-timestamp", "-id"]