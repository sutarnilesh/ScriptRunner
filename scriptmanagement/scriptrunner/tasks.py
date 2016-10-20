import subprocess

from djcelery import celery
from celery import task
from models import Rule


@task
def executerule(ruleid):
    print ruleid
    try:
        rule = Rule.objects.get(pk=ruleid)
        filetoexecute = rule.filelocation
        command = ["python", filetoexecute]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        return stdout
    except Exception as error:
        return error
