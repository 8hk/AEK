import json

from django.test import TestCase

from api.search.views import SearchHelper

class TestSearchMethods(TestCase):
    def setUp(self):
        main_query = ""
        self.search_helper = SearchHelper(main_query)

    def test_search_combinations(self):
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
