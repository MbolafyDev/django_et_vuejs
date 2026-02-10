# articles/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Article
from .serializers import ArticleSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # ✅
def articles_list_create(request):
    if request.method == "GET":
        qs = Article.objects.all()
        serializer = ArticleSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = ArticleSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        obj = serializer.save()
        return Response(ArticleSerializer(obj, context={"request": request}).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # ✅
def article_detail(request, pk: int):
    obj = get_object_or_404(Article, pk=pk)

    if request.method == "GET":
        return Response(ArticleSerializer(obj, context={"request": request}).data, status=status.HTTP_200_OK)

    if request.method in ["PUT", "PATCH"]:
        serializer = ArticleSerializer(
            obj,
            data=request.data,
            partial=(request.method == "PATCH"),
            context={"request": request},
        )
        if serializer.is_valid():
            obj = serializer.save()
            return Response(ArticleSerializer(obj, context={"request": request}).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    obj.delete()
    return Response({"detail": "Article supprimé."}, status=status.HTTP_200_OK)
