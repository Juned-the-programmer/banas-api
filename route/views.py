from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .serializers import *
from django.http import JsonResponse
from rest_framework import status

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
        return JsonResponse({"error_message" : "Route already Exists ! "} , status=status.HTTP_400_BAD_REQUEST)
      else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  if request.method == 'GET':
    route = Route.objects.all()
    serializer = RouteSerializerGET(route , many=True)
    
    return JsonResponse(serializer.data , status=status.HTTP_200_OK , safe=False)

  return JsonResponse({
    'message' : "Something went wrong, Please try again ! "
  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET' , 'PUT'])
@permission_classes([IsAdminUser, IsAuthenticated])
def list_update_route(request, pk):
  if request.method == 'GET':
    try:
      route = Route.objects.get(id=pk)
      route_serializer = RouteSerializer(route)
      return JsonResponse(route_serializer.data)
    except Route.DoesNotExist:
      return JsonResponse({
        'message' : "Route is not valid, Check once again ! "
      }, status=status.HTTP_404_NOT_FOUND)

  if request.method == 'PUT':
    try:
      route = Route.objects.get(id=pk)
      serializer = RouteSerializer(route , data=request.data)
      if serializer.is_valid():
        serializer.save(updatedby = request.user.username)
        return JsonResponse(serializer.data , status=status.HTTP_200_OK)

    except Route.DoesNotExist:
      return JsonResponse({
        'message' : "Route Doesn't Exists !"
      }, status=status.HTTP_400_BAD_REQUEST)

  return JsonResponse({
    'message' : "Something went wrong, Please try again later"
  }, status = status.HTTP_400_BAD_REQUEST)