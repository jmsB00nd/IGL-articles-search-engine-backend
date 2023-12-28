from elasticsearch_dsl import Text,Document,Keyword,Date,Integer

class ArticleIndex(Document):
    titre = Text()
    auteurs = Text()
    institutions = Text()
    resume = Text()
    contenu = Text()
    references = Text()
    motsCles = Text()
    urlPDF = Keyword()
    pathPDF = Keyword()
    publication_date = Date()
    likes = Integer()
    search = Integer()

    class Index:
        name = "articles_index"