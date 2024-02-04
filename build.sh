docker run -d --name elasticsearch -v //srv/elas1:/usr/share/elasticsearch/data -p 9200:9200 -p 9300:9300 -e "ELASTICSEARCH_HEAP_SIZE=512m" bitnami/elasticsearch &&
docker run -d --name cermine -p 8072:8080 elifesciences/cermine:1.13 &&
docker build -t tp-igl-backend . &&
docker run -d -p 8000:8000 tp-igl-backend
