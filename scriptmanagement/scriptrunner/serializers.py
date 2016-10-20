

from rest_framework import serializers
from models import Rule, RuleExecutionSummary #RuleScheduler

#class RuleSchedulerSerializer(serializers.ModelSerializer):
#	class Meta:
#		model = RuleScheduler
#		fields = ('id', 'schedulertime', 'schedulertype')


class RuleSerializer(serializers.ModelSerializer):
	#scheduler = RuleSchedulerSerializer()
	class Meta:
		model = Rule
		fields = ('id', 'rulename', 'schedulertype','datafile','filelocation', 'created', 'hours', 'minutes')


class RuleExecutionSummarySerializer(serializers.ModelSerializer):
	class Meta:
		model = RuleExecutionSummary
		depth = 1
		fields = ('rulename', 'ruleid', 'starttime', 'stoptime', 'status', 'filelocation', 'error_message')
