import concurrent
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
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
from django.http import HttpResponse, HttpResponseRedirect
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from api.mainquery.views import Dimension
import os
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
import os


@csrf_exempt
def startSearch(request):
    if request.method == "POST":
        print("post")
        main_query = request.POST.get("main_query")
        dimensions = request.POST.get("dimensions")
        print("main: ", main_query)
        print("dimensions: ", dimensions)
        dimensions_json = json.loads(dimensions)["dimensions"]
        resp = Search.search_annotated_articles(main_query, dimensions_json)
        resp["dimensions"]=dimensions_json
        resp["mainquery"]=main_query

        data = {}
        data["keyword_pairs"] = json.dumps(resp)
        request.session['keyword_pairs'] = data
        return HttpResponseRedirect(reverse("summaryPage"))


def highlight(text, start, end):
    return text[:start] + '<span style="background-color: #FFFF00">' + text[start:end] + '</span>' + text[end:]


def annotations(request, articleId):
    if request.method == "GET":
        annotationId = request.GET.get("annotationId")

        mongo_client = MongoClient(
            host='mongodb:27017',  # <-- IP and port go here
            serverSelectionTimeoutMS=3000,  # 3 second timeout
            username='root',
            password='mongoadmin',
        )
        db = mongo_client["mentisparchment_docker"]

        title = ""
        authors = ""
        keywords = ""
        abstract = ""
        column = db["annotated_article_ids"]
        query = {"id": str(articleId)}
        articles = column.find(query)
        for item in articles:
            list_item = dict(item)
            title = list_item["title"]
            authors = list_item["author_list"]
            keywords = list_item["top_three_keywords"]
            abstract = list_item["abstract"]
            break

        authors_str = "; ".join(authors)

        # Check whether an annotation id is given.
        if annotationId is None:
            return render(request, "html/article.html",
                          {"title": title, "authors": authors_str, "abstract": abstract})
        else:
            pm_id = ""
            column = db["annotation_to_article"]
            query = {"annotation_id": int(annotationId)}
            annotation_to_article = column.find(query)
            for item in annotation_to_article:
                list_item = dict(item)
                pm_id = list_item["pm_id"]
                break

            # Check whether the given annotation is related to the given article.
            if pm_id != "" and pm_id == str(articleId):
                print("Such annotation exists for such article")
                start = 0
                end = 0
                column = db["annotation"]
                query = {"id": int(annotationId)}
                annotations = column.find(query)
                for item in annotations:
                    list_item = dict(item)
                    start = list_item["target"]["selector"]["start"]
                    end = list_item["target"]["selector"]["end"]

                # Find which part of the article this annotation is from.
                if start < len(title):
                    title = highlight(title, start, end)
                elif start < len(title + authors_str):
                    offset = len(title)
                    authors_str = highlight(authors_str, start - offset, end - offset)
                else:
                    offset = len(title + authors_str)
                    abstract = highlight(abstract, start - offset, end - offset)

                return render(request, "html/article.html",
                              {"title": title, "authors": authors_str, "keywords": keywords,
                               "abstract": abstract})
            else:
                print("This annotation is not related to this article")
                return render(request, "html/article.html",
                              {"title": title, "authors": authors_str, "keywords": keywords, "abstract": abstract})


class Search:
    @staticmethod
    def search_annotated_articles(main_query, dimensions_json):
        helper = SearchHelper(main_query)
        helper.create_search_combinations(dimensions_json)
        helper.create_search_keys()
        articles = helper.start_query()
        del helper
        return articles


class SearchHelper(object):
    mongo_client = ""
    db = ""
    annotation_column = ""
    annotation_detail_column = ""
    articles = []
    article_details = {}
    search_result_list = []
    articles_by_term = {}

    def __init__(self, main_query):
        self.es_url = os.environ.get("ELASTIC_SEARCH_SERVICE_URL", " ")
        self.es_port = os.environ.get("ELASTIC_SEARCH_SERVICE_PORT", 443)
        self.es_username = os.environ.get("ELASTIC_SEARCH_SERVICE_USERNAME", " ")
        self.es_password = os.environ.get("ELASTIC_SEARCH_SERVICE_PASSWORD", " ")
        self.main_query = main_query.lower()
        self.dimensions = []
        self.combinations = []
        # we will use this later while parsing the articles
        self.all_terms = []
        self.search_result_list = []
        self.articles_by_term = {}

        self.mongo_client = MongoClient(
            host='mongodb:27017',  # <-- IP and port go here
            username='root',
            password='mongoadmin',
            maxPoolSize=2000
        )
        self.db = self.mongo_client["mentisparchment_docker"]
        self.annotation_column = self.db["annotation"]
        self.annotation_detail_column = self.db["annotated_article_ids"]

    def start_annotations(self, combination):
        common_article_list = []
        print("new combination", combination)
        # split the combination list
        combination_line = combination.split(")")
        urls = []
        if len(combination_line) > 1:
            for each_keyword_combination in combination_line:
                if len(each_keyword_combination) > 0:
                    urls.append(self.articles_by_term[each_keyword_combination])
            common_article_list = list(set.intersection(*map(set, urls)))
        elif len(combination_line) == 1:
            common_article_list = self.articles_by_term[combination_line[0]]
        print("common article list created for ", combination, " total article list ", len(common_article_list))
        if len(common_article_list) > 0:
            article_details_futures = []
            articles = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                article_details_futures.append(executor.submit(self.get_article_details, common_article_list))
                for x in as_completed(article_details_futures):
                    articles = x.result()
            print("articles created for ", combination)
            if len(articles) > 0:
                search_result = SearchResult(combination)
                search_result.add_articles(articles)
                SearchResult.summary_articles(search_result, articles)
                print("articles summarized for ", combination)
                self.search_result_list.append(search_result)
                del search_result
                del articles
        else:
            search_result = SearchResult(combination)
            search_result.empty_result=True
            self.search_result_list.append(search_result)
        common_article_list.clear()

    def start_query(self):
        search_result_list = []
        response = {}
        response["keyword_pairs"] = []
        for keyword in self.all_terms:
            # query annotations by keyword retrieve article id
            # query elastic by keyword retrieve article id
            # combine them together without duplicate
            # append combined list into articles_by_term
            article_list_from_annotation = self.get_article_ids_from_annotations(keyword)
            article_list_from_elastic = self.get_article_ids_from_elastic_with_proximity_and_fuzzy(keyword)
            article_list_from_annotation_as_set = set(article_list_from_annotation)
            article_list_from_elastic_as_set = set(article_list_from_elastic)
            list_elastic_items_not_in_list_annotation = list(
                article_list_from_elastic_as_set - article_list_from_annotation_as_set)
            combined = article_list_from_annotation + list_elastic_items_not_in_list_annotation
            del article_list_from_annotation
            del article_list_from_elastic
            del article_list_from_elastic_as_set
            self.articles_by_term[keyword] = combined

        if len(self.combinations) > 0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.combinations)) as executor:
                futures = []
                for combination in self.combinations:
                    futures.append(executor.submit(self.start_annotations, combination))
        dict_futures = []
        work_num = 0
        if len(self.search_result_list) > 0:
            work_num = len(self.search_result_list)
        else:
            work_num = 1
        #sort search result list
        self.search_result_list.sort(key=lambda x: x.number_of_article, reverse=False)
        with concurrent.futures.ThreadPoolExecutor(max_workers=work_num) as executor:
            while self.search_result_list:
                dict_futures.append(executor.submit(self.search_result_list.pop().generate_dict_value, response))
        for x in as_completed(dict_futures):
            print("dict value created")
        return response

    def create_search_combinations(self, dimensions_json):
        for dimension in dimensions_json:
            dimension_obj = Dimension()
            for keyword in dimension['keywords']:
                dimension_obj.add_keyword(keyword.lower())
            self.dimensions.append(dimension_obj)
        self.start_parsing()

    def start_parsing(self):
        dimension_number = len(self.dimensions)
        for i in range(dimension_number):
            self.start_keyword_pairing(dimension_number, i)
        if len(self.main_query) > 0:
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

    def elastic_search(self, main_query):
        #es = Elasticsearch(hosts=["es01"])
        es = Elasticsearch(hosts=[self.es_url], http_auth=(self.es_username, self.es_password), port=self.es_port, use_ssl=True)

        res = es.search(
            index="test8",
            body={
                "query": {
                    "match": {
                        "abstract": main_query
                    }
                }
            }
        )

        print("Got %d Hits:" % res['hits']['total']['value'])
        for hit in res['hits']['hits']:
            print("%(_created)s %(title)s by %(authors)s (%(keywords)s): %(abstract)s" % hit["_source"])

    # we dont need to retrieve all retrieve for each key again and again. instead we will use this list while
    # retrieving the articles
    def create_search_keys(self):
        self.all_terms.append(self.main_query)
        for dimension_line in self.dimensions:
            for keyword in dimension_line.keywords:
                self.all_terms.append(keyword)

    # takes article ids from mongodb with its keyword
    def get_article_ids_from_annotations(self, keyword):
        query = {}
        article_id_list = []
        query["body.items.value"] = keyword
        document = self.annotation_column.find(query)
        for x in document:
            list_item = dict(x)
            target_id_str = list_item["target"]["id"].split("/")
            if target_id_str[len(target_id_str) - 1] not in article_id_list:
                article_id_list.append(target_id_str[len(target_id_str) - 1])
        return article_id_list

    # returns a dict that consist all articles in the mongodb
    def retrieve_all_articles(self):
        mongo_query = {}
        document = self.annotation_detail_column.find(mongo_query)
        all_papers = {}
        for x in document:
            list_item = dict(x)
            all_papers[list_item["id"]] = list_item
        return all_papers

    # takes article details from mongodb with its keyword
    def article_details_query(self, article_id):
        mongo_query = {}
        mongo_query["id"] = article_id
        document = self.annotation_detail_column.find(mongo_query)
        for x in document:
            list_item = dict(x)
            article = Article(pm_id=list_item["id"],
                              title=list_item["id"],
                              journal_issn="",
                              journal_name=list_item["journal_name"],
                              abstract="",
                              pubmed_link=list_item["pubmed_link"],
                              author_list=list_item["author_list"],
                              instutation_list=list_item["institution_list"],
                              article_date=list_item["article_date"],
                              top_three_keywords=list_item["top_three_keywords"])
            del list_item
            del document
            return article

    # create collection of details of articles
    def get_article_details(self, article_list):
        articles = []
        all_articles = self.retrieve_all_articles()
        # create all articles from given list
        for article_id in article_list:
            list_item = all_articles[article_id]
            if article_id == list_item["id"]:
                article = Article(pm_id=list_item["id"],
                                  title=list_item["title"],
                                  journal_issn="",
                                  journal_name=list_item["journal_name"],
                                  abstract="",
                                  pubmed_link=list_item["pubmed_link"],
                                  article_link=os.environ.get("ARTICLE_URL", " ") + "/articles/" + list_item["id"],
                                  author_list=list_item["author_list"],
                                  instutation_list=list_item["institution_list"],
                                  article_date=list_item["article_date"],
                                  top_three_keywords=list_item["top_three_keywords"],
                                  article_type=list_item["article_type"])
                articles.append(article)
        return articles

    def get_article_ids_from_elastic(self, keyword):
        #es = Elasticsearch(hosts=["es01"])
        es = Elasticsearch(hosts=[self.es_url], http_auth=(self.es_username, self.es_password), port=self.es_port, use_ssl=True)
        res = es.search(
            index="test8",
            body={
                "query": {
                    "multi_match":
                        {"query": keyword,
                         "fields": ["abstract", "keywords"]
                         }
                }
            }
        )
        result = []
        for hit in res['hits']['hits']:
            result.append(hit["_source"]['article_id'])
        del res
        return result

    def find_stored_article_number(self):
        mongo_query = {}
        document = self.annotation_detail_column.find(mongo_query)
        unique_papers = []
        for x in document:
            list_item = dict(x)
            if list_item["id"] not in unique_papers:
                unique_papers.append(list_item["id"])
        return len(unique_papers)

    def find_annotation_size(self):
        mongo_query = {}
        document = self.annotation_column.find(mongo_query)
        return document.count()


    def get_article_ids_from_elastic_with_proximity(self, keyword):
        slop_option=4
        #es = Elasticsearch(hosts=["es01"])
        es = Elasticsearch(hosts=[self.es_url], http_auth=(self.es_username, self.es_password), port=self.es_port, use_ssl=True)
        res = es.search(
            index="test8",
            body={
                "query": {
                    "match_phrase": {
                        "abstract": {"query": keyword,
                                    "slop": slop_option
                                    }
                    }

                }
            }
        )
        result = []
        for hit in res['hits']['hits']:
            result.append(hit["_source"]['article_id'])
        del res

        res = es.search(
            index="test8",
            body={
                "query": {
                    "match_phrase": {
                        "keywords": {"query": keyword,
                                     "slop": slop_option
                                     }
                    }

                }
            }
        )
        for hit in res['hits']['hits']:
            result.append(hit["_source"]['article_id'])
        del res

        return result

    #this method allows us to search keyword fuzzy and proximity features of elastic
    #proximity means there can be several keywords between subkeywords
    #fuzzy means, user may mistype the keyword
    def get_article_ids_from_elastic_with_proximity_and_fuzzy(self,keyword):
        #es = Elasticsearch(hosts=["es01"])
        es = Elasticsearch(hosts=[self.es_url], http_auth=(self.es_username, self.es_password), port=self.es_port, use_ssl=True)
        body= self.fuzzy_proximity_search_creator("abstract",keyword)
        json_res=body
        res = es.search(
            index="test8",
            body=json_res
        )
        result = []
        for hit in res['hits']['hits']:
            result.append(hit["_source"]['article_id'])
        del res

        body = self.fuzzy_proximity_search_creator("keywords", keyword)
        json_res = body
        res = es.search(
            index="test8",
            body=json_res
        )
        for hit in res['hits']['hits']:
            result.append(hit["_source"]['article_id'])
        del res
        return result

    def fuzzy_proximity_search_creator(self,type,keyword):
        clauses=[]
        slop_option = 5
        fuzziness=2
        in_order="true"
        keyword_list=keyword.split(" ")
        for subkeyword in keyword_list:
            clause={
                        "span_multi":{
                           "match":{
                              "fuzzy":{
                                 type:{
                                    "value":subkeyword,
                                    "fuzziness":fuzziness
                                 }
                              }
                           }
                        }
                     }
            clauses.append(clause)

        resp = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "span_near": {
                                "clauses": clauses,
                                "slop": slop_option,
                                "in_order":in_order
                            }
                        }
                    ]
                }
            }
        }

        return json.dumps(resp)


# it is similar class with annotate_abstract
class Article(object):

    def __init__(self, pm_id, title, journal_issn, journal_name, abstract, pubmed_link, article_link, author_list,
                 instutation_list, article_date, top_three_keywords, article_type):
        self.pm_id = pm_id
        self.title = title
        self.journal_issn = journal_issn
        self.journal_name = journal_name
        self.abstract = abstract
        self.pubmed_link = pubmed_link
        self.article_link=article_link
        self.author_list = author_list
        self.instutation_list = instutation_list
        self.article_date = article_date
        self.top_three_keywords = top_three_keywords
        self.article_type = article_type
        self.json_val = self.toJSON()

    def toJSON(self):
        return {
            "pm_id": self.pm_id,
            "title": self.title,
            "authors": self.author_list,
            "pubmed_link": self.pubmed_link,
            "article_link":self.article_link,
            "article_type": self.article_type,
            "article_date": self.article_date
        }


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
        self.number_of_article = 0
        self.articles = []
        self.top_keywords = []
        self.top_authors = []
        self.result_change_time_years = []
        self.result_change_time_numbers = []
        self.pm_ids = []
        self.authors = []
        self.empty_result=False

    def change_article_number(self, article_number):
        self.number_of_article = article_number

    def add_article(self, article):
        self.articles.append(article)

    def add_articles(self, articles):
        for article in articles:
            self.articles.append(article)

    def add_author(self, author):
        self.authors.append(author)

    def add_top_authors(self, authors):
        for author in authors:
            self.top_authors.append(author)

    def add_top_keyword(self, keyword):
        self.top_keywords.append(keyword)

    def add_top_keywords(self, keywords):
        for keyword in keywords:
            self.top_keywords.append(keyword)

    def add_year(self, year):
        self.result_change_time_years.append(year)

    def add_years(self, years):
        for year in years:
            self.result_change_time_years.append(year)

    def add_number_of_year(self, number):
        self.result_change_time_numbers.append(number)

    def add_number_publication_per_years(self, numbers):
        for number in numbers:
            self.result_change_time_numbers.append(number)

    def generate_json_value(self):
        s1 = "{"
        s3 = "}"
        str = f'"value":{self.keyword.replace(")", " ")},"papers_number":{self.number_of_article},"top_authors":{self.top_authors},"top_keywords":{self.top_keywords},"publication_year":{self.result_change_time_years},"publication_year_values":{self.result_change_time_numbers}'
        return s1 + str + s3

    def generate_dict_value(self, response):
        dict = {}
        json_articles = []
        for article in self.articles:
            json_articles.append(article.json_val)
        dict["value"] = self.keyword.replace(")", ",")
        dict["papers_number"] = self.number_of_article
        dict["top_authors"] = self.top_authors
        dict["top_keywords"] = self.top_keywords
        dict["publication_year"] = self.result_change_time_years
        dict["publication_year_values"] = self.result_change_time_numbers
        dict["articles"] = json_articles
        dict["empty_result"] = self.empty_result
        del json_articles
        response["keyword_pairs"].append(dict)
        del dict

    # collects the articles and prepares them for the search result operation
    @staticmethod
    def summary_articles(search_result, articles):
        top_keywords = SearchResult.get_top_keywords_of_articles(articles)
        # top_authors =[]
        top_authors = SearchResult.get_top_authors_of_articles(articles)
        time_change_dict = SearchResult.get_time_change_of_articles(articles)
        time_change_list = list(time_change_dict.items())
        years = [i[0] for i in time_change_list]
        number_publication_per_year = [i[1] for i in time_change_list]
        total_articles = len(articles)
        search_result.change_article_number(total_articles)
        search_result.add_years(years)
        search_result.add_number_publication_per_years(number_publication_per_year)
        search_result.add_top_authors(top_authors)
        search_result.add_top_keywords(top_keywords)

    # finds the 3 top keywords among the articles
    @staticmethod
    def get_top_keywords_of_articles(articles):
        abstracts = ""
        top_keywords = []
        top_3_keywords = {}
        for article in articles:
            # abstracts += article.abstract
            for keyword in article.top_three_keywords:
                if keyword in top_3_keywords:
                    val = top_3_keywords[keyword] + len(article.abstract)
                    top_3_keywords.update({keyword: val})
                else:
                    top_3_keywords[keyword] = len(article.abstract)
        return sorted(top_3_keywords, key=top_3_keywords.get, reverse=True)[:3]

    # finds the 3 top authors among the articles
    @staticmethod
    def get_top_authors_of_articles(articles):
        all_authors = []
        for article in articles:
            for author in article.author_list:
                all_authors.append(author)

        most_common_authors = [word for word, word_count in Counter(all_authors).most_common(3)]
        del all_authors
        return most_common_authors

    # calculates the publication dates among the articles and sorts them max to min
    @staticmethod
    def get_time_change_of_articles(articles):
        dates = {}
        for article in articles:
            if len(article.article_date) > 0:
                if article.article_date not in dates:
                    dates[article.article_date] = 1
                else:
                    dates[article.article_date] += 1
        return dict(sorted(dates.items(), key=lambda item: int(item[0]), reverse=False))


def page(request):
    return render(request, 'html/index.html')


def summaryPage(request):
    args = request.session.get('keyword_pairs')
    return render(request, 'html/summary-page.html', args)


def findArticleNumber():
    helper = SearchHelper("")
    return helper.find_stored_article_number()

# how many article stored into mongodb
def findStoredArticleNumber(request):
    dict= findArticleNumber()
    # return render(request,json.dumps(dict))
    return HttpResponse(json.dumps(dict), content_type="application/json")


def findAnnotationNumber():
    helper = SearchHelper("")
    return helper.find_annotation_size()
