from elasticsearch_dsl import Text,Document,Keyword,Integer

class ArticleIndex(Document):
    id = Keyword()
    title = Text()
    authors = Keyword(multi=True)
    institutions = Keyword(multi=True)
    resume = Text()
    content = Text()
    references = Keyword(multi=True)
    keywords = Keyword(multi=True)
    urlPDF = Keyword()
    publication_date = Keyword()

    class Index:
        name = "articles_index"