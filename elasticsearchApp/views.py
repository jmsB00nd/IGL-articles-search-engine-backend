from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .utils import (
    download_pdf_from_url,
    process_pdf_file,
)  # Assume you put the function in a file named utils.py
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import connections, Document, Text, Keyword
from .serializers import ArticleIndexSerializer
from .search_indexes import ArticleIndex

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])


def download_pdf(request, url):
    file_name = download_pdf_from_url(url)

    if file_name:
        # Do something with the downloaded file, like serving it as a response or further processing
        metadata = process_pdf_file(file_name)
        try:
            os.remove(file_name)
        except OSError as e:
            print(f"Error deleting file: {e}")

        if metadata:
            # You can customize the response format as needed
            response_data = {
                "title": metadata["title"],
                "authors": metadata["authors"],
                "institutions": metadata["institutions"],
                "keywords": metadata["keywords"],
                "abstract": metadata["abstract"],
                "text": metadata["text"],
                "references": metadata["references"],
            }

            # Return the metadata as a JSON response
            return JsonResponse(response_data)
        else:
            return HttpResponse("Failed to extract metadata.", status=500)

    else:
        return HttpResponse("Failed to download the file.", status=500)


@api_view(['POST'])
def add_article(request):
    # Deserialize the request data using the serializer
    serializer = ArticleIndexSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Create an<Route path="/" element={<GererArticle />} /> instance of the ArticleIndex document
    article_document = ArticleIndex(**serializer.validated_data)

    # Save the document to Elasticsearch
    article_document.save()

    # Return a JSON response indicating success
    return Response({'status': 'success'})