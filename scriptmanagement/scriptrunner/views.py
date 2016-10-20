import subprocess

from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse

from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser

from models import Rule, TaskScheduler
from serializers import RuleSerializer

from tasks import executerule

# Create your views here.

class RuleViewSet(viewsets.ModelViewSet):
	queryset = Rule.objects.all()
	serializer_class = RuleSerializer
	parser_classes = (MultiPartParser, FormParser,)

	def list(self, request, format=None):
		serializer = self.serializer_class(self.queryset, many=True)
		return Response(serializer.data)

	def create(self, request, format=None):
		datafile = request.FILES.get('datafile')
		if not datafile:
			return Response(status=404)
		#request.data.pop("datafile")
		serializer = RuleSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			filelocation = serializer.instance.datafile.path
			serializer.instance.filelocation=filelocation
			serializer.instance.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def get_object(pk):
	try:
		return Rule.objects.get(pk=pk)
	except Rule.DoesNotExist:
		return Http404
		
class RuleDetail(APIView):
	"""
	Retrive, update or delete a rule instance.
	"""

	def get(self, request, pk, format=None):
		rule = get_object(pk)
		serializer = RuleSerializer(rule)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		import pdb;pdb.set_trace()
		rule = get_object(pk)
		serializer = RuleSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			filelocation = serializer.instance.datafile.path
			serializer.instance.filelocation=filelocation
			serializer.instance.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	
	def delete(self, request, pk, format=None):
		rule = get_object(pk)
		rule.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def ruleexecuter(request, pk):
	#import pdb;pdb.set_trace()
	#rule = get_object(pk)
	TaskScheduler.schedule_every(executerule, 'minutes', 1, pk)
	#result = executerule.delay(rule)
	#from time import sleep
	#sleep(3)
	#if result.successful():
	#	status = {"task_id": result.id, "status": result.status, "filepath": result.result.strip(), "state": result.state};
	#else:
	#	status = {"task_id": result.id, "status": result.status, 'error': result.traceback, "state": result.state}
	#return Response(status, status=200)
