from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
# desired operation below
# m -> x?
# d1 -> a b
# d2 -> c
# d3 ->d e
#
#
#
# 1. x
# 2. x a
# 3. x a c
# 4. x a c d
# 5. x a c e
# 6. x b
# 7. x b c
# 8. x b c d
# 9. x b c e
import json
from django.http import HttpResponse
from datetime import datetime
from elasticsearch import Elasticsearch

from api.mainquery.views import Dimension
from api.search.models import AnnotatedArticle

STATIC_JSON = """
{
    "dimensions":[
        {
                    "keywords": [
                        "a","b","c","d"
                    ]
                },
        {
                    "keywords": [
                        "e","f"
                    ]
                },
        {
                    "keywords": [
                        "g","h"
                    ]
                }
    ]
}
"""

STATIC_JSON_2 = """
{
    "dimensions":[
        {
                    "keywords": [
                        "a","b"
                    ]
                },
        {
                    "keywords": [
                        "c"
                    ]
                },
        {
                    "keywords": [
                        "d"
                    ]
                },
        {
                    "keywords": [
                        "e"
                    ]
                },
        {
                    "keywords": [
                        "f","g"
                    ]
                }
    ]
}
"""

STATIC_JSON_3 = """
{
    "main_query":"happiness",
    "dimensions":[
        {
                    "keywords": [
                        "bipolar","genetics"
                    ]
                },
        {
                    "keywords": [
                        "manic depressive"
                    ]
                }
    ]
}
"""

@csrf_exempt
def detail(request):
    if request.method == "POST":
        print("post")
        main_query = request.POST.get("main_query")
        dimensions = request.POST.get("dimensions")
        print("main: ", main_query)
        print("dimensions: ", dimensions)
        dimensions_json = json.loads(dimensions)["dimensions"]

        resp = Search.search_annotated_articles(main_query, dimensions_json)
        return HttpResponse("%s" % resp)


class Search:
    @staticmethod
    def search_annotated_articles(main_query, dimensions_json):
        helper = SearchHelper(main_query)
        helper.create_search_combinations(dimensions_json)
        articles = helper.get_annotations()
        helper.elastic_search()
        del helper
        return articles


class SearchHelper(object):
    def __init__(self, main_query):
        self.main_query = main_query
        self.dimensions = []
        self.combinations = []

    def get_annotations(self):
        articles = {}
        if len(self.combinations) > 0:
            for combination in self.combinations:
                bodylist = AnnotatedArticle.objects.filter(body_value=combination)
                articles[combination] = []
                for body in bodylist:
                    articles[combination].append(body.target)
            return articles

    def create_search_combinations(self, dimensions_json):
        for dimension in dimensions_json:
            dimension_obj = Dimension()
            for keyword in dimension['keywords']:
                dimension_obj.add_keyword(keyword)
            self.dimensions.append(dimension_obj)
        self.start_parsing()

    def start_parsing(self):
        dimension_number = len(self.dimensions)
        for i in range(dimension_number):
            self.start_keyword_pairing(dimension_number, i)
        self.combinations.append(self.main_query)
        print("All search combinations: ", self.combinations)

    def start_keyword_pairing(self, dimension_number, current_index):
        # iterate for all keyword for each dimension
        for keyword in self.dimensions[current_index].keywords:
            if len(self.main_query) > 0:
                keyword = self.main_query + " " + keyword
            self.combinations.append(keyword)
            current_keyword_pairing = ""
            # other_dimension_index means the index from another dimensions
            for other_dimension_index in range(dimension_number):
                # a-> c already done c->a or a->b should not walk again and again!
                if other_dimension_index == current_index or other_dimension_index < current_index:
                    pass
                else:
                    # other_dimension_keyword means the keyword from another dimensions
                    for other_dimension_keyword in self.dimensions[other_dimension_index].keywords:
                        another_inside_str = ""
                        # check it is last element
                        if current_index != dimension_number - 1:
                            current_keyword_pairing = keyword + " " + other_dimension_keyword
                            self.combinations.append(current_keyword_pairing)
                            # iterate through 6th dimension!
                            self.iterate_keyword_pairing(current_keyword_pairing, dimension_number, current_index,
                                                         keyword,
                                                         other_dimension_keyword,
                                                         other_dimension_index, 1)

    def iterate_keyword_pairing(self, current_keyword_pairing, dimension_number, current_index, keyword,
                                other_dimension_keyword,
                                other_dimension_index,
                                index):
        # 6th dimension hardcoded!
        if other_dimension_index != dimension_number - index and index != 6:
            for next_keyword in self.dimensions[other_dimension_index + index].keywords:
                new_keyword_pairing = current_keyword_pairing + " " + next_keyword
                self.combinations.append(new_keyword_pairing)
                # new_keyword_pairing becomes another inside str
                self.iterate_keyword_pairing(new_keyword_pairing, dimension_number, current_index, keyword,
                                             other_dimension_keyword,
                                             other_dimension_index, index + 1)

    def elastic_search(self):
        es = Elasticsearch(hosts=["es01"])

        doc = {
            'author': 'first last',
            'title': 'title',
            'abstract': 'abstract goes here',
            'timestamp': datetime.now(),
        }
        res = es.index(index="test-index", id=1, body=doc)
        print(res['result'])

        res = es.get(index="test-index", id=1)
        print(res['_source'])

        es.indices.refresh(index="test-index")

        res = es.search(
            index="test-index",
            body={
                "query": {
                    "match": {
                        "abstract": "goes"
                    }
                }
            }
        )
        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print("%(timestamp)s %(author)s: %(abstract)s" % hit["_source"])

def page(request):
    return render(request, 'html/index.html')