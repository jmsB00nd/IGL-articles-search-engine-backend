from django.http import HttpResponse, JsonResponse
from .utils import (
    download_pdf_from_url,
    process_pdf_file,
    download_pdf_from_drive
) 
import os
from rest_framework.decorators import api_view
from elasticsearch_dsl import connections,Search
from .search_indexes import ArticleIndex
from .models import Article

# Define your Elasticsearch connection
connections.create_connection(hosts=['http://localhost:9200'])

def get_data_elasticsearch(request):
    # Create a Search object on the ArticleIndex
    search = Search(index=ArticleIndex.Index.name)

    # Execute the search and retrieve all documents
    response = search.execute()

    # Extract data from the search response
    data = []
    for hit in response.hits:
        data.append({
            "title": hit.title,
            "authors": list(hit.authors),  
            "institutions": list(hit.institutions), 
            "keywords": list(hit.keywords),  
            "abstract": hit.resume,
            "text": hit.content,
            "references": list(hit.references), 
            "urlPDF": hit.urlPDF,
        })

    # Return the data as a JSON response
    return JsonResponse(data, safe=False)


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
            article_model = Article.objects.create(likes=0,search=0)
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

