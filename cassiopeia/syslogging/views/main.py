from django.http.response import HttpResponse
from django.shortcuts import render
import datetime

def syslogging(request):
    return render(request, 'syslogging.html',context={"project_name":"System Logging"})