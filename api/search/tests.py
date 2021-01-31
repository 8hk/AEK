import json

from django.test import TestCase

from api.search.views import SearchHelper

class TestSearchMethods(TestCase):
    def setUp(self):
        main_query = "main query"
        self.search_helper = SearchHelper(main_query)

    def test_search_combinations_parsing(self):
        # given
        dimensions = '{"dimensions":[{"keywords": ["keyword1", "keyword2"]},{"keywords": ["keyword3"]}]}'
        dimensions_json = json.loads(dimensions)["dimensions"]

        # when
        self.search_helper.create_search_combinations(dimensions_json)

        # then
        dim1 = self.search_helper.dimensions[0].keywords
        dim2 = self.search_helper.dimensions[1].keywords
        self.assertEqual(dim1[0], "keyword1")
        self.assertEqual(dim1[1], "keyword2")
        self.assertEqual(dim2[0], "keyword3")

    def test_search_combinations_parsing(self):
        # given
        dimensions = '{"dimensions":[{"keywords": ["keyword1", "keyword2"]},{"keywords": ["keyword3"]}]}'
        dimensions_json = json.loads(dimensions)["dimensions"]

        # when
        self.search_helper.create_search_combinations(dimensions_json)

        # then
        self.assertEqual(self.search_helper.combinations[0], "main query)keyword1")
        self.assertEqual(self.search_helper.combinations[1], "main query)keyword1)keyword3")
        self.assertEqual(self.search_helper.combinations[2], "main query)keyword2")
        self.assertEqual(self.search_helper.combinations[3], "main query)keyword2)keyword3")
        self.assertEqual(self.search_helper.combinations[4], "main query)keyword3")
        self.assertEqual(self.search_helper.combinations[5], "main query")
