from django.shortcuts import render

# Create your views here.

class MainQuery(object):

    def __init__(self):
        self.dimensions = []

    def add_dimension(self, dimension):
        self.dimensions.append(dimension)

    def add_keyword(self, dimension,keyword):
        self.dimensions[dimension].append(keyword)

    def print_main_query(self):
        for dimension in self.dimensions:
            print(dimension.print_dimension() + "\n")


class Dimension(object):
    def __init__(self):
        self.keywords = []

    def add_keyword(self, keyword):
        self.keywords.append(keyword)

    def print_dimension(self):
        print(self.keywords)

