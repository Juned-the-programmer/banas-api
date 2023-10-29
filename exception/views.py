from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from .error_constant import *

# Create your views here.
def not_found_exception(error_message):
    return JsonResponse({
        'error' : error_message
    }, status = NOT_FOUND)

def internal_server_error():
    return JsonResponse({
        'error' : INTERAL_SERVER_ERROR_MESSAGE
    }, status = INTERNAL_SERVER_ERROR)
