from django.http import HttpResponse, JsonResponse
from .utils import (
    download_pdf_from_url,
    process_pdf_file,
    download_pdf_from_drive
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 
from django.shortcuts import get_object_or_404,get_list_or_404
import os
from rest_framework.decorators import api_view
from elasticsearch_dsl import connections,Search
from .search_indexes import ArticleIndex
from .models import Article
from PaperHub.models import PaperHubUser
from django.contrib.auth.models import User

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])


api_view(['GET']) 
@permission_classes([IsAuthenticated])
def get_data_elasticsearch(request):
    # Create a Search object on the ArticleIndex
    search = Search(index=ArticleIndex.Index.name)

    # Execute the search and retrieve all documents
    response = search.execute()

    # Extract data from the search response
    data = []
    for hit in response.hits:
        data.append({
            "id" : hit.id,
            "title": hit.title,
            "authors": list(hit.authors),
            "keywords": list(hit.keywords),
            "institutions": list(hit.institutions),
        })

    # Return the data as a JSON response
    return JsonResponse(data, safe=False)



@permission_classes([IsAuthenticated])
def get_articles_mod(request):
    search = Search(index=ArticleIndex.Index.name)
    response = search.execute()
    data = []
    for hit in response.hits:
        article = get_object_or_404(Article, pk=hit.id)
        data.append({
            "id" : hit.id,
            "title": hit.title,
            "authors": list(hit.authors),
            "approved" : article.approved   
        })
    
    return JsonResponse(data,safe=False) 
    

@permission_classes([IsAuthenticated])
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
            article_model = Article.objects.create(likes=0,search=0,approved=True)
            article = ArticleIndex(
                id=article_model.id, 
                title=metadata["title"],
                authors=metadata["authors"],
                institutions=metadata["institutions"],
                resume=metadata["abstract"],
                content=metadata["text"],
                references=metadata["references"],
                keywords=metadata["keywords"],
                urlPDF=url,
            )

            article.save()
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
    
@permission_classes([IsAuthenticated])
def download_pdf_drive(request, id):
    full_url = f"https://drive.google.com/uc?export=download&id={id}"
    file_name = download_pdf_from_drive(full_url)
    if file_name:
        # Do something with the downloaded file, like serving it as a response or further processing
        metadata = process_pdf_file(file_name)
        try:
            os.remove(file_name)
        except OSError as e:
            print(f"Error deleting file: {e}")

        if metadata:
            article_model = Article.objects.create(likes=0,search=0,approved=True)
            article = ArticleIndex(
                id=article_model.id, 
                title=metadata["title"],
                authors=metadata["authors"],
                institutions=metadata["institutions"],
                resume=metadata["abstract"],
                content=metadata["text"],
                references=metadata["references"],
                keywords=metadata["keywords"],
                urlPDF=full_url,
            )

            article.save()
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
    
@permission_classes([IsAuthenticated])
def delete_article(request, article_id):
    try:
        search = Search(index='articles_index').query('term', id=article_id)
        response = search.execute()
        if response.hits.total.value > 0:
            doc_id = response.hits[0].meta.id
            article = ArticleIndex.get(id=doc_id)
            article.delete()

            article_model = Article.objects.get(id=article_id)
            article_model.delete()
            return JsonResponse({'message': f'Article with id {article_id} deleted successfully.'})
        else:
            return JsonResponse({'message': f'Article with id {article_id} not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    



api_view(['GET'])    
@permission_classes([IsAuthenticated])
def search_articles(request,search_query):
    if request.method == 'GET':
        try:
            search = Search(index=ArticleIndex.Index.name).query('multi_match', query=search_query ,  fields=['title', 'authors', 'resume', 'content','institutions','references','keywords'])
            response = search.execute()
            hits = response.hits
            data = [
                {
                    "id": hit.id,
                    "title": hit.title,
                    "authors": list(hit.authors),
                    "keywords": list(hit.keywords),
                    "institutions": list(hit.institutions),
                    "resume": hit.resume[0: 200],
                } for hit in hits
            ]

            return JsonResponse(data, safe=False)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

api_view(['GET']) 
@permission_classes([IsAuthenticated])
def get_article_by_id(request, article_id):
    try:
        search = Search(index='articles_index').query('term', id=article_id)
        response = search.execute()

        if response.hits.total.value > 0:
            hit = response.hits[0]
            data = {
                "id": hit.id,
                "title": hit.title,
                "references" : list(hit.references) if hasattr(hit, 'references') and hit.references is not None else [],
                "content" : hit.content,
                "institutions" : list(hit.institutions),
                "keywords" : list(hit.keywords),
                "resume" : hit.resume,
                "authors": list(hit.authors),
                "urlPDF": hit.urlPDF,
                # Add other fields as needed
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'message': f'Article with id {article_id} not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

api_view(['GET'])    
@permission_classes([IsAuthenticated])
def get_favourite(request, user_id):
    try:
        user_profile = get_object_or_404(User, pk=user_id)
        paperhub_user = PaperHubUser.objects.get(user=user_profile)
        favorite_articles = paperhub_user.favorite_articles.all()
        articles_details = []

        for article in favorite_articles:
            search = Search(index=ArticleIndex.Index.name)
            search = search.query("term", id=article.id)
            response = search.execute()
            if response.hits.total.value > 0:
                article_details = {
                    'id': response.hits[0].id,
                    'title': response.hits[0].title,
                    'resume': response.hits[0].resume,
                }
                articles_details.append(article_details)

        return JsonResponse({'favorite_articles': articles_details}, status=200)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except PaperHubUser.DoesNotExist:
        return JsonResponse({'error': 'PaperHubUser not found'}, status=404)