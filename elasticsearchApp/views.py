from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import connections, Document, Text, Keyword
from .serializers import ArticleIndexSerializer
from .search_indexes import ArticleIndex

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])

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