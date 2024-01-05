from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from .error_constant import *

# Create your views here.
def customer_not_found_exception(customer_id):
    return JsonResponse({
        'error' : CUSTOMER_NOT_FOUND.format(customer_id)
    }, status = NOT_FOUND)

def route_not_found_exception(route_id):
    return JsonResponse({
        'error' : ROUTE_NOT_FOUND.format(route_id)
    }, status=NOT_FOUND)

def route_already_exists():
    return JsonResponse({
        'error' : ROUTE_ALREADY_EXISTS
    }, status=BAD_REQUEST)

def internal_server_error():
    return JsonResponse({
        'error' : INTERAL_SERVER_ERROR_MESSAGE
    }, status = INTERNAL_SERVER_ERROR)

def serializer_errors(error):
    return JsonResponse({
        'error' : error
    }, status = BAD_REQUEST)