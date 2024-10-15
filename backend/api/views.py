from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Example
from .serializer import ExampleSerializer

# Create your views here. This should contain all the actual functions run during an API call

@api_view(['GET'])
def get_example(request):
    return Response(ExampleSerializer({'name':'John'}).data)