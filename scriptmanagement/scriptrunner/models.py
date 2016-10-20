from __future__ import unicode_literals

import os

from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from djcelery.models import PeriodicTask, IntervalSchedule


# Create your models here.

FILEUPLOADPATH = os.path.join(settings.MEDIA_ROOT, settings.MEDIA_URL)
	
def user_directory_path(instance, filename):
	#import pdb;pdb.set_trace()
	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	#return 'user_{0}/{1}'.format(instance.user.id, filename) 
	return 'user_{0}/{1}'.format('admin', filename) 

class Rule(models.Model):
	rulename = models.CharField("rulename", max_length=30, unique=True)
	datafile = models.FileField(max_length=10000)
	filelocation = models.CharField("filelocation", max_length=255, default=True)
	created = models.DateTimeField(auto_now_add=True)
	#scheduler = models.ForeignKey('RuleScheduler', related_name='rules', on_delete=models.CASCADE, null=False, blank=False)
	#schedulertime = models.TimeField('schedulertime', default=datetime.now)
	hours = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(24)])
	minutes = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(60)])
        schedulertype = models.CharField("schedulertype", max_length=20)
	

	class Meta:
		db_table = 'rules'


#class RuleScheduler(models.Model):
#	schedulertime = models.DateTimeField('schedulertime', default=datetime.now)
#        schedulertype = models.CharField("schedulertype", max_length=20)
#
#	class Meta:
#		db_table = 'rulescheduler'


class RuleExecutionSummary(models.Model):
	rulename = models.CharField("rulename", max_length=30) 
	ruleid = models.PositiveIntegerField("ruleid")
	starttime = models.DateTimeField("starttime", default=datetime.now)
	stoptime = models.DateTimeField("stoptime", default=datetime.now)
	status = models.CharField("status", max_length=20)
	filelocation = models.CharField("filelocation", max_length=255)
	error_message = models.CharField("error_message", max_length=255)
	
	class Meta:
		db_table = "ruleexecutionsummary"

class TaskScheduler(models.Model):
    
    periodic_task = models.ForeignKey(PeriodicTask)

    @staticmethod
    def schedule_every(task_name, period, every, args=None, kwargs=None):
    	"""
	schedules a task by name every "every" "period". So an example call would be:
        TaskScheduler('mycustomtask', 'seconds', 30, [1,2,3]) 
        that would schedule your custom task to run every 30 seconds with the arguments 1,2 and 3 passed to the actual task. 
    	"""
        permissible_periods = ['days', 'hours', 'minutes', 'seconds']
        if period not in permissible_periods:
            raise Exception('Invalid period specified')
        # create the periodic task and the interval
        ptask_name = "%s_%s" % (task_name, datetime.now()) # create some name for the period task
        interval_schedules = IntervalSchedule.objects.filter(period=period, every=every)
        if interval_schedules: # just check if interval schedules exist like that already and reuse em
            interval_schedule = interval_schedules[0]
        else: # create a brand new interval schedule
            interval_schedule = IntervalSchedule()
            interval_schedule.every = every # should check to make sure this is a positive int
            interval_schedule.period = period 
            interval_schedule.save()
        ptask = PeriodicTask(name=ptask_name, task=task_name, interval=interval_schedule)
        if args:
            ptask.args = args
        if kwargs:
            ptask.kwargs = kwargs
        ptask.save()
        return TaskScheduler.objects.create(periodic_task=ptask)

    def stop(self):
        ptask = self.periodic_task
        ptask.enabled = False
        ptask.save()

    def start(self):
        ptask = self.periodic_task
        ptask.enabled = True
        ptask.save()

    def terminate(self):
        self.stop()
        ptask = self.periodic_task
        self.delete()
        ptask.delete()
