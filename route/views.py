from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from rest_framework import status
from exception.views import *

# Create your views here.
@api_view(['GET' , 'POST'])
@permission_classes([IsAdminUser, IsAuthenticated])
def RouteListView(request):
  if request.method == 'POST':
    serializer = RouteSerializer(data = request.data)
    if serializer.is_valid():
      serializer.save(addedby = request.user.username)
      return JsonResponse(serializer.data , status=status.HTTP_201_CREATED)
    else:
      errors = serializer.errors
      if 'route_name' in errors:
        return route_already_exists()
      else:
        return serializer_errors(serializer.errors)

  if request.method == 'GET':
    route = Route.objects.all()
    serializer = RouteSerializerGET(route , many=True)
    
    return JsonResponse(serializer.data , status=status.HTTP_200_OK , safe=False)

  return internal_server_error()

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_update_route(request, pk):
  if request.method == 'GET':
    try:
      route = Route.objects.get(id=pk)
    except Route.DoesNotExist:
      return route_not_found_exception(pk)

    route_serializer = RouteSerializerGET(route)
    return JsonResponse(route_serializer.data)
    
  if request.method == 'PUT':
    serializer = RouteSerializer(route , data=request.data)
    if serializer.is_valid():
      serializer.save(updatedby = request.user.username)
      return JsonResponse(serializer.data , status=status.HTTP_200_OK)
    else: 
      errors = serializer.errors
      if 'route_name' in errors:
        return route_already_exists()
      else:
        return serializer_errors(serializer.errors)

  return internal_server_error()