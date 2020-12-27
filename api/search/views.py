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
        helper = SearchHelper()
        resp = helper.get_annotations(dimensions_json)
        return HttpResponse("%s" % resp)


class SearchHelper(object):
    def __init__(self):
        self.dimensions = []
        self.search_terms = []

    def get_annotations(self, dimensions):
        dimension_objs = []
        print(dimensions)
        for dimension in dimensions:
            dimension_obj = Dimension()
            for keyword in dimension['keywords']:
                dimension_obj.add_keyword(keyword)
            dimension_objs.append(dimension_obj)
            self.dimensions.append(dimension_obj)
        print(dimensions)
        self.create_search_terms()
        resp = {}
        if len(self.search_terms) > 0:
            for term in self.search_terms:
                bodylist = AnnotatedArticle.objects.filter(body_value=term)
                resp[term] = []
                for body in bodylist:
                    resp[term].append(body.target)
        return resp

    def start_keyword_pairing(self, dimension_number, current_index):
        # iterate for all keyword for each dimension
        for keyword in self.dimensions[current_index].keywords:
            self.search_terms.append(keyword)
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
                            self.search_terms.append(current_keyword_pairing)
                            # iterate through 6th dimension!
                            self.iterate_keyword_pairing(current_keyword_pairing, dimension_number, current_index,
                                                         keyword,
                                                         other_dimension_keyword,
                                                         other_dimension_index, 1)

    def iterate_keyword_pairing(self, current_keyword_pairing, dimension_number, current_index, keyword,
                                other_dimension_keyword,
                                other_dimension_index,
                                index):
        new_keyword_pairing = ""
        # 6th dimension hardcoded!
        if other_dimension_index != dimension_number - index and index != 6:
            for next_keyword in self.dimensions[other_dimension_index + index].keywords:
                new_keyword_pairing = current_keyword_pairing + " " + next_keyword
                self.search_terms.append(new_keyword_pairing)
                # new_keyword_pairing becomes another inside str
                self.iterate_keyword_pairing(new_keyword_pairing, dimension_number, current_index, keyword,
                                             other_dimension_keyword,
                                             other_dimension_index, index + 1)

    def create_search_terms(self):
        dimension_number = len(self.dimensions)
        current_index = 0
        for i in range(dimension_number):
            self.start_keyword_pairing(dimension_number, i)
        print(self.search_terms)


def page(request):
    return render(request, 'html/index.html')