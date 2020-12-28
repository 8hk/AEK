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
from pymongo import MongoClient

from api.mainquery.views import Dimension
from api.search.models import AnnotatedArticle
from django.template.response import TemplateResponse
import pymongo
import collections
from nltk import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import requests
import xmltodict
from collections import Counter
import sys


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
    "main_query":"",
    "dimensions":[
        {
                    "keywords": [
                        "bipolar disorder"
                    ]
                },
        {
                    "keywords": [
                        "entity"
                    ]
                }
    ]
}
"""

STATIC_JSON_4 = """
{
    "main_query":"symptom",
    "dimensions":[
        {
                    "keywords": [
                        "treatment"
                    ]
                },
        {
                    "keywords": [
                        "role","personality"
                    ]
                }
    ]
}
"""
STATIC_SUMMARY_JSON = """
{
    "keyword_pairs":[
        {
            "value":"bipolar disorder",
            "papers_number":1200,
            "top_authors":["William Anot","John Doe","Jack Spar"],
            "top_keywords":["attention ","autism","spectrum"],
            "publication_year":[2020,2019,2018,2017,2003,1992],
            "publication_year_values":[20,500,400,150,50,200]
        },
        {
            "value":"manic depressive",
            "papers_number":1350,
            "top_authors":["Adam Rot","Sarah Lats","Abbie Dur"],
            "top_keywords":["suicidal","disorder","behavior"],
            "publication_year":[2017,2016,2015,2014],
            "publication_year_values":[200,800,1000,1500]
        },
        {
            "value":"bipolar disorder-manic depressive" ,
            "papers_number":350,
            "top_authors":["Adele Codre","Niche Dur","Agatha Cirs"],
            "top_keywords":["disease","circadian","hallucination"],
            "publication_year":[2017,2016,2015,2014],
            "publication_year_values":[600,800,300,450]
        }
    ]
}
"""


@csrf_exempt
def detail(request):
    # if request.method == "POST":
    #     print("post")
    #     main_query = request.POST.get("main_query")
    #     dimensions = request.POST.get("dimensions")
    #     print("main: ", main_query)
    #     print("dimensions: ", dimensions)
    #     dimensions_json = json.loads(dimensions)["dimensions"]
    #
    #     resp = Search.search_annotated_articles(main_query, dimensions_json)
    #     return HttpResponse("%s" % resp)


    args = {}
    args['mytext'] = STATIC_SUMMARY_JSON
    return TemplateResponse(request, 'html/summary-page.html', args)



class Search:
    @staticmethod
    def search_annotated_articles(main_query, dimensions_json):
        helper = SearchHelper(main_query)
        helper.create_search_combinations(dimensions_json)
        helper.create_search_keys()
        articles = helper.get_annotations()
        del helper
        return articles


class SearchHelper(object):
    mongo_client = ""
    db = ""
    column = ""
    articles = []

    def __init__(self, main_query):
        self.main_query = main_query
        self.dimensions = []
        self.combinations = []
        # we will use this later while parsing the articles
        self.all_terms = []

        self.mongo_client = MongoClient(
            host='mongodb:27017',  # <-- IP and port go here
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            username='root',
            password='mongoadmin',
        )
        self.db = self.mongo_client["mentisparchment_docker"]
        self.column = self.db["annotation"]

    def get_annotations(self):
        articles_by_term = {}
        search_result_list=[]
        response=""
        for keyword in self.all_terms:
            article_list = self.get_article_ids(keyword)
            articles_by_term[keyword] = article_list

        if len(self.combinations) > 0:
            for combination in self.combinations:
                common_article_list = []
                # split the combination list
                combination_line = combination.split(")")
                urls = []
                if len(combination_line) > 1:
                    for each_keyword_combination in combination_line:
                        if len(each_keyword_combination) > 0:
                            # urls[each_keyword_combination]=self.get_article_ids(each_keyword_combination)
                            urls.append(articles_by_term[each_keyword_combination])
                    common_article_list = list(set.intersection(*map(set, urls)))
                elif len(combination_line) == 1:
                    common_article_list = articles_by_term[combination_line[0]]
                self.get_article_details(common_article_list)
                search_result = SearchResult(combination)
                search_result.add_articles(self.articles)
                Article.summary_articles(search_result,self.articles)
                search_result_list.append(search_result)
        for search_result in search_result_list:
            response+=search_result.generate_json_value()
        return response

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
                keyword = self.main_query + ")" + keyword
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
                            current_keyword_pairing = keyword + ")" + other_dimension_keyword
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
                new_keyword_pairing = current_keyword_pairing + ")" + next_keyword
                self.combinations.append(new_keyword_pairing)
                # new_keyword_pairing becomes another inside str
                self.iterate_keyword_pairing(new_keyword_pairing, dimension_number, current_index, keyword,
                                             other_dimension_keyword,
                                             other_dimension_index, index + 1)

    # we dont need to retrieve all retrieve for each key again and again. instead we will use this list while
    # retrieving the articles
    def create_search_keys(self):
        self.all_terms.append(self.main_query)
        for dimension_line in self.dimensions:
            for keyword in dimension_line.keywords:
                self.all_terms.append(keyword)

    #takes article details from mongodb with its keyword
    def get_article_ids(self, combination):
        query = {}
        query["body.value.id"] = combination
        document = self.column.find(query)
        article_id_list = []
        for x in document:
            list_item = dict(x)
            if list_item["target"]["id"] not in article_id_list:
                article_id_list.append(list_item["target"]["id"])
        return article_id_list

    #collects the details of articles
    def get_article_details(self, article_list):
        for article_id in article_list:
            article = Article.retrieve_article(article_id)
            article.abstract = article.get_abstract_text(article.abstract)
            # article.get_top_keywords()
            self.articles.append(article)

def page(request):
    return render(request, 'html/index.html')

#it is similar class with annotate_abstract
class Article:
    pm_id = ""
    title = ""
    abstract = ""
    journal_issn = ""
    journal_name = ""
    pubmed_link = ""
    author_list = []
    instutation_list = []
    article_date = ""
    top_three_keywords = []

    def __init__(self, pm_id, title, journal_issn, journal_name, abstract, pubmed_link, author_list, instutation_list,
                 article_date):
        self.pm_id = pm_id
        self.title = title
        self.journal_issn = journal_issn
        self.journal_name = journal_name
        self.abstract = abstract
        self.pubmed_link = pubmed_link
        self.author_list = author_list
        self.instutation_list = instutation_list
        self.article_date = article_date

    #fetch article from entrez
    @staticmethod
    def retrieve_article(article_id):
        response = requests.get(EntrezGetArticleRequest(article_id))
        if response.ok:
            try:
                xpars = xmltodict.parse(response.text)
                article = xpars["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
                article_title = article["ArticleTitle"]
                journal_issn = article["Journal"]["ISSN"]["#text"]
                journal_name = article["Journal"]["Title"]
                pubmed_link = "https://pubmed.ncbi.nlm.nih.gov/" + str(article_id) + "/"
                abstract = article["Abstract"]["AbstractText"]

                author_list_text = article["AuthorList"]['Author']


                author_list = []
                instutation_list = []


                #TODO
                #author list has some problems. some list has one author some has many author
                #but parsing is quite difficult. it should be tested. for some articles below algorithm not working
                #that's why its closed

                # if len(author_list_text)>4 or type(author_list_text) == list:
                #     for author_info in author_list_text:
                #         if len(author_info)>2:
                #             instute_name = ""
                #             name = author_info['ForeName'] + " " + author_info['LastName']
                #             author_list.append(name)
                #             if author_info.get("AffiliationInfo") is not None:
                #                 if (len(author_info['AffiliationInfo']) > 1):
                #                     for affiliationInfo in author_info['AffiliationInfo']:
                #                         instute_name += affiliationInfo['Affiliation'] + " "
                #                 else:
                #                     instute_name += author_info['AffiliationInfo']['Affiliation']
                #                 instutation_list.append(instute_name)
                #             else:
                #                 instutation_list.append("")
                #
                #     if article.get("ArticleDate") is not None:
                #         articledate = article["ArticleDate"]
                #         article_date = articledate['Year']
                #     else:
                #         article_date =""
                # else:
                #     author_info =author_list_text
                #     instute_name = ""
                #     name = author_info['ForeName'] + " " + author_info['LastName']
                #     author_list.append(name)
                #     if author_info.get("AffiliationInfo") is not None:
                #         if (len(author_info['AffiliationInfo']) > 1):
                #             for affiliationInfo in author_info['AffiliationInfo']:
                #                 instute_name += affiliationInfo['Affiliation'] + " "
                #         else:
                #             instute_name += author_info['AffiliationInfo']['Affiliation']
                #         instutation_list.append(instute_name)
                #     else:
                #         instutation_list.append("")

                if article.get("ArticleDate") is not None:
                    articledate = article["ArticleDate"]
                    article_date = articledate['Year']
                else:
                    article_date = ""

                return Article(article_id, article_title, journal_issn, journal_name, abstract, pubmed_link,
                               author_list,
                               instutation_list, article_date)
            except:
                print("Oops!", sys.exc_info()[0], "occurred for article id: ", article_id)
        else:
            print("\tArticle could not be retrieved.")

    #collects the articles and prepares them for the search result operation
    @staticmethod
    def summary_articles(search_result,articles):
        # top_keywords = Article.get_top_keywords_of_articles(articles)
        # top_authors = Article.get_top_authors_of_articles(articles)
        # time_change_dict = Article.get_time_change_of_articles(articles)
        top_keywords = []
        top_authors = []
        time_change_dict =  Article.get_time_change_of_articles(articles)
        time_change_list = list(time_change_dict.items())[:5]
        years = [i[0] for i in time_change_list]
        number_publication_per_year = [i[1] for i in time_change_list]
        total_articles= len(articles)



        search_result.change_article_number(total_articles)
        search_result.add_years(years)
        search_result.add_number_publication_per_years(number_publication_per_year)
        search_result.add_top_authors(top_authors)
        search_result.add_top_keywords(top_keywords)


    #finds the 3 top keywords among the articles
    @staticmethod
    def get_top_keywords_of_articles(articles):
        abstracts = ""
        top_keywords = []
        for article in articles:
            abstracts += article.abstract
        abstracts = abstracts.translate(str.maketrans('', '', string.punctuation))
        stopword = set(stopwords.words('english'))
        # tokenize
        word_tokens = word_tokenize(abstracts)
        # remove stopwords
        removing_stopwords = [word for word in word_tokens if word not in stopword]
        # find most common words
        fdist = FreqDist(removing_stopwords)
        print("most common ", fdist.most_common(3))
        for most_common in fdist.most_common(3):
            top_keywords.append(most_common)
        return top_keywords

    # finds the 3 top authors among the articles
    @staticmethod
    def get_top_authors_of_articles(articles):
        all_authors = []
        for article in articles:
            for author in article.author_list:
                all_authors.append(all_authors)

        most_common_authors = [word for word, word_count in Counter(all_authors).most_common(3)]
        del all_authors
        return most_common_authors

    # calculates the publication dates among the articles and sorts them max to min
    @staticmethod
    def get_time_change_of_articles(articles):
        dates = {}
        for article in articles:
            if article.article_date not in dates:
                dates[article.article_date] = 1
            else:
                dates[article.article_date] += 1
        return sorted(dates, key=dates.get, reverse=True)

    #finds top 3 keywords of an article
    def get_top_keywords(self):
        # remove punctiotions
        s = self.abstract
        s = s.translate(str.maketrans('', '', string.punctuation))
        stopword = set(stopwords.words('english'))
        # tokenize
        word_tokens = word_tokenize(s)
        # remove stopwords
        removing_stopwords = [word for word in word_tokens if word not in stopword]
        # find most common words
        fdist = FreqDist(removing_stopwords)
        print("most common ", fdist.most_common(3))
        for most_common in fdist.most_common(3):
            self.top_three_keywords.append(most_common[0])

    def get_authors(self):
        return self.author_list

    #abstract retrieve helper
    def get_abstract_text(self, unparsed_abstract_text):
        abstract_text = ""
        if type(unparsed_abstract_text) == list:
            for x in unparsed_abstract_text:
                if type(x) == str:
                    abstract_text += x
                else:
                    abstract_text += self.get_abstract_text(x)
                    '''
                    for key, value in x.items():
                        if key=='#text':
                            abstract_text+=value
                    '''
        elif type(unparsed_abstract_text) == collections.OrderedDict:
            for key, value in unparsed_abstract_text.items():
                if key == '#text':
                    abstract_text += value
        elif type(unparsed_abstract_text) == str:
            abstract_text = unparsed_abstract_text
        return abstract_text




class Author(object):
    name_surname: ""
    institute = ""

    def __init__(self, name, Institute):
        self.name_surname = name
        self.institute = Institute


class Institute(object):
    name: ""
    location: ""

    def __init__(self, name, location):
        self.name = name
        self.location = location


class TopKeyword(object):
    top_keyword = ""

    def __init__(self, top_keyword):
        self.top_keyword = top_keyword


class SearchResult(object):
    keyword = ""
    number_of_article = 0
    articles = []
    top_keywords = []
    top_authors = []
    result_change_time_years = []
    result_change_time_numbers = []
    pm_ids = []
    authors = []

    def __init__(self, keyword):
        self.keyword = keyword

    def change_article_number(self, article_number):
        self.number_of_article = article_number

    def add_article(self, article):
        self.articles.append(article)

    def add_articles(self, articles):
        for article in articles:
            self.articles.append(article)

    def add_author(self, author):
        self.authors.append(author)

    def add_top_authors(self,authors):
        for author in authors:
            self.authors.append(author)

    def add_top_keyword(self, keyword):
        self.top_keywords.append(keyword)

    def add_top_keywords(self, keywords):
        for keyword in keywords:
            self.top_keywords.append(keyword)

    def add_year(self, year):
        self.result_change_time_years.append(year)

    def add_years(self,years):
        for year in years:
            self.result_change_time_years.append(year)

    def add_number_of_year(self, number):
        self.result_change_time_numbers.append(number)

    def add_number_publication_per_years(self,numbers):
        for number in numbers:
            self.result_change_time_numbers.append(number)

    def generate_json_value(self):
        str = f"""
        {
        "value":"{self.keyword}",
            "papers_number":{self.number_of_article},
            "top_authors":{self.top_authors},
            "top_keywords":{self.top_keywords},
            "publication_year":{self.result_change_time_years},
            "publication_year_values":{self.result_change_time_numbers}
        }
        """
        return str



class EntrezGetArticleRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    article_id = 0

    def __init__(self, article_id):
        self.article_id = article_id

    def __str__(self):
        return self.base_url + "efetch.fcgi?db=pubmed&id=" + self.article_id + "&retmode=xml"

