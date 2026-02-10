# client/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny

from .models import Client
from .serializers import ClientSerializer

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def clients_list_create(request):
    if request.method == "GET":
        qs = Client.objects.all()
        return Response(ClientSerializer(qs, many=True).data)

    serializer = ClientSerializer(data=request.data)
    if serializer.is_valid():
        obj = serializer.save()
        return Response(ClientSerializer(obj).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def client_detail(request, pk):
    obj = get_object_or_404(Client, pk=pk)

    if request.method == "GET":
        return Response(ClientSerializer(obj).data)

    if request.method in ["PUT", "PATCH"]:
        serializer = ClientSerializer(obj, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            obj = serializer.save()
            return Response(ClientSerializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response({"detail": "Client supprimé."})

