#############################################################################################################
#   Retrieves Pudmed Articles                                                                               #
#                                                                                                           #
#   Entrez REST API:                                                                                        #
#   https://eutils.ncbi.nlm.nih.gov/entrez/eutils/                                                          #
#                                                                                                           #
#   Example:                                                                                                #
#   https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science[journal]              #
#   +AND+breast+cancer+AND+2008[pdat]                                                                       #
#                                                                                                           #
#############################################################################################################

import requests
import xmltodict
import collections
import re
import pickle
import os
from pymongo import MongoClient
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime
import concurrent
from elasticsearch import Elasticsearch, helpers
import uuid

lock = threading.Lock()
import collections
from nltk import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

client = MongoClient(
    host=os.environ.get("MONGO_DB_HOST", " ") + ":" + os.environ.get("MONGO_DB_PORT", " "),  # <-- IP and port go here
    serverSelectionTimeoutMS=3000,  # 3 second timeout
    username=os.environ.get("MONGO_DB_USERNAME", " "),
    password=os.environ.get("MONGO_DB_PASSWORD", " "),
)

db = client[os.environ.get("MONGO_INITDB_DATABASE", " ")]

annotation_url = os.environ.get("ARTICLE_URL", " ")

detailed_article_list = []
already_inserted_detailed_article_id_list = []

# import ontology_retriever as onRe
# print("Retrieving all concepts in the following list of ontologies: ", onRe.list_of_bioportal_ontologies)
# concepts = onRe.retrieve_annotations(API_KEY, max_page_limit=10)
infile = open('concepts.pickle', 'rb')
concepts = pickle.load(infile)
infile.close()

search_keywords = ["bipolar disorder", "manic depression", "bipolar", "manic depression disorder"]
number_of_article = 50

annotation_list = []

articles = []


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
    uri = ""

    def __init__(self, pm_id, title, journal_issn, journal_name, abstract,
                 pubmed_link, author_list, instutation_list, article_date,article_type):
        self.pm_id = pm_id
        self.title = title
        self.journal_issn = journal_issn
        self.journal_name = journal_name
        self.abstract = abstract
        self.pubmed_link = pubmed_link
        self.author_list = author_list
        self.instutation_list = instutation_list
        self.article_date = article_date
        self.top_three_keywords = []
        self.article_type = article_type

    # finds top 3 keywords of an article's abstract
    def get_top_keywords(self):
        # remove punctiotions
        s = ""
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


class EntrezSearchRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_term = ""
    max_article_limit = 20

    def __init__(self, search_term, max_article_limit):
        self.search_term = search_term
        self.max_article_limit = max_article_limit

    def __str__(self):
        return self.base_url + "esearch.fcgi?db=pubmed&term=" + self.search_term + "&retmax=" + str(
            self.max_article_limit)


class EntrezGetAbstractRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    article_id = 0

    def __init__(self, article_id):
        self.article_id = article_id

    def __str__(self):
        return self.base_url + "efetch.fcgi?db=pubmed&id=" + self.article_id + "&retmode=text&rettype=abstract"


class EntrezGetArticleRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    article_id = 0

    def __init__(self, article_id):
        self.article_id = article_id

    def __str__(self):
        return self.base_url + "efetch.fcgi?db=pubmed&id=" + self.article_id + "&retmode=xml"


def retrieve_article_ids(search_term, max_article_limit):
    try:
        response = requests.get(EntrezSearchRequest(search_term, max_article_limit))

        if response.ok:
            xpars = xmltodict.parse(response.text)
            article_count = xpars['eSearchResult']['Count']
            returned_article_id_count = int(xpars['eSearchResult']['RetMax'])
            print("From " + article_count + " articles " + str(
                returned_article_id_count) + " article ids are retrieved")
            return xpars['eSearchResult']['IdList']['Id']
        else:
            print("\tThis article id could not be retrieved.")
    except:
        print("something related with ", sys.exc_info(), " definitely happened")


def get_abstract_of_given_article_id(article_id):
    response = requests.get(EntrezGetAbstractRequest(article_id))

    if response.ok:
        return response.text
    else:
        print("\tThis article abstract could not be retrieve for given id.")


def retrieve_article(article_id):
    response = requests.get(EntrezGetArticleRequest(article_id))
    if response.ok:
        try:
            xpars = xmltodict.parse(response.text)
            article = ""
            article_title = ""
            journal_issn = ""
            journal_name = ""
            pubmed_link = ""
            abstract = ""
            author_list_text = []
            author_list = []
            instutation_list = []
            articledate = ""
            article_date = ""
            article_type=""
            if xpars.get("PubmedArticleSet") is not None:
                if xpars.get("PubmedArticleSet").get('PubmedArticle') is not None:
                    if xpars.get("PubmedArticleSet").get('PubmedArticle').get("MedlineCitation") is not None:
                        if xpars.get("PubmedArticleSet").get('PubmedArticle').get("MedlineCitation").get(
                                "Article") is not None:
                            article = xpars["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
                            if article.get("ArticleTitle") is not None:
                                article_title = article["ArticleTitle"]

                            if article.get("Journal") is not None:
                                if article.get("Journal").get('ISSN') is not None:
                                    if article.get("Journal").get('ISSN').get("#text") is not None:
                                        journal_issn = article["Journal"]["ISSN"]["#text"]
                                if article.get("Journal").get('Title') is not None:
                                    journal_name = article["Journal"]["Title"]

                            pubmed_link = "https://pubmed.ncbi.nlm.nih.gov/" + str(article_id) + "/"
                            if article.get("Abstract") is not None:
                                if article.get("Abstract").get('AbstractText') is not None:
                                    abstract = article["Abstract"]['AbstractText']

                            if article.get("AuthorList") is not None:
                                if article.get("AuthorList").get('Author') is not None:
                                    author_list_text = article["AuthorList"]['Author']

                                    if len(author_list_text) > 4 or type(author_list_text) == list:
                                        for author_info in author_list_text:
                                            if len(author_info) > 2:
                                                instute_name = ""
                                                name = author_info['ForeName'] + " " + author_info['LastName']
                                                author_list.append(name)
                                                if author_info.get("AffiliationInfo") is not None:
                                                    if (len(author_info['AffiliationInfo']) > 1):
                                                        for affiliationInfo in author_info['AffiliationInfo']:
                                                            instute_name += affiliationInfo['Affiliation'] + " "
                                                    else:
                                                        instute_name += author_info['AffiliationInfo']['Affiliation']
                                                    instutation_list.append(instute_name)
                                                else:
                                                    instutation_list.append("")

                                        if article.get("ArticleDate") is not None:
                                            articledate = article["ArticleDate"]
                                            article_date = articledate['Year']
                                        else:
                                            article_date = ""
                                    elif len(author_list_text) == 1:
                                        author_info = author_list_text
                                        instute_name = ""
                                        name = author_info['ForeName'] + " " + author_info['LastName']
                                        author_list.append(name)
                                        if author_info.get("AffiliationInfo") is not None:
                                            if (len(author_info['AffiliationInfo']) > 1):
                                                for affiliationInfo in author_info['AffiliationInfo']:
                                                    instute_name += affiliationInfo['Affiliation'] + " "
                                            else:
                                                instute_name += author_info['AffiliationInfo']['Affiliation']
                                            instutation_list.append(instute_name)
                                        else:
                                            instutation_list.append("")

                            if article.get("ArticleDate") is not None:
                                articledate = article["ArticleDate"]
                                article_date = articledate['Year']
                            else:
                                article_date = ""

                            if article.get("PublicationTypeList") is not None:
                                if article.get("PublicationTypeList").get("PublicationType") is not None:
                                    article_type=article["PublicationTypeList"]["PublicationType"]["#text"]

                            return Article(article_id, article_title, journal_issn, journal_name, abstract, pubmed_link,
                                           author_list,
                                           instutation_list, article_date,article_type)
        except:
            print("Oops!", sys.exc_info(), "occurred for article id: ", article_id)
            print("Details about article:", article_title, " journal_issn:", journal_issn, " journal_name: ",
                  journal_name, " pubmed_link:", pubmed_link, " author_list", author_list, " instutation_list",
                  instutation_list,
                  " article_date:", article_date)
            print("Oops!", sys.exc_info()[0], "occurred for article id: ", article_id)


def get_abstract_text(unparsed_abstract_text):
    abstract_text = ""
    if type(unparsed_abstract_text) == list:
        for x in unparsed_abstract_text:
            if type(x) == str:
                abstract_text += x
            else:
                abstract_text += get_abstract_text(x)
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


def annotate(retrieved_article_ids):
    new_article_counter = 0
    annotation_counter_start = get_annotation_counter_start()
    annotation_counter = annotation_counter_start
    if len(retrieved_article_ids) > 0:
        for idx in range(0, len(retrieved_article_ids)):
            try:
                lock.acquire()
                print("Retrieving articles with pubmed id=" + str(retrieved_article_ids[idx]))
                article = retrieve_article(retrieved_article_ids[idx])
                article.abstract = get_abstract_text(article.abstract)
                # Ignore an article if it is already annotated.
                if article.pm_id in already_inserted_detailed_article_id_list:
                    print("Article ", article.pm_id, " is already annotated.")
                    continue
                else:
                    new_article_counter += 1
                    article.get_top_keywords()
                    detailed_article_object = create_detailed_article_object(article)
                    already_inserted_detailed_article_id_list.append(article.pm_id)
                    detailed_article_list.append(detailed_article_object)

                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    future = executor.submit(write_details_into_database)
                    result = future.result()
                # print(str(id)+"\n")
                # print(article.abstract)
                for c in concepts:
                    positions = get_index_positions(article.title, c.pref_label, offset=0)
                    author_list_str = " ".join(article.author_list)
                    positions.extend(get_index_positions(author_list_str, c.pref_label, offset=len(article.title)))
                    positions.extend(get_index_positions(article.abstract, c.pref_label,
                                                         offset=len(article.title + author_list_str)))
                    if positions:
                        for position in positions:
                            # print("ONTOLOGY CONCEPT: " + c.pref_label + " POSITION START:" + str(position['start']) + " POSITION END:" + str(position['end']) + "\n")
                            # print("Article with id: " + retrieved_article_ids[id] + " has ontolgy concept: " + c.id + " (synonyms=" + c.pref_label + ")")
                            article.uri = annotation_url + "/articles/" + article.pm_id
                            annotation_object = create_annotation_object(annotation_counter, article, c, position)
                            if article.pm_id not in annotated_article_ids:
                                annotated_article_ids.append(article.pm_id)
                            # print(annotation_object)
                            annotation_counter = annotation_counter + 1
                            annotation_list.append((annotation_object, article.pm_id))
                            if len(annotation_list) > 0:
                                write_annotations_to_database(annotation_list)
                        print("\n--------------------------------------------")

                article_json = {
                    "id": article.pm_id,
                    "title": article.title,
                    "authors": article.author_list,
                    "keywords": article.top_three_keywords,
                    "abstract": article.abstract.lower(),
                    "article_date": article.article_date,
                    "journal_name": article.journal_name,
                    "article_id": article.pm_id,
                    "_created": datetime.now()
                }
                articles.append(article_json)

            except:
                print("Oops!", sys.exc_info(), "occurred.")
            finally:
                lock.release()
    print("Number of new articles: ", new_article_counter)
    print("Number of new annotations: ", annotation_counter - annotation_counter_start)
    return convert_to_json_abjects(annotated_article_ids)


def convert_to_json_abjects(annotated_article_ids):
    annotated_article_ids_json = []
    for i in annotated_article_ids:
        annotated_article_ids_json.append({'id': i})
    return annotated_article_ids_json


def get_index_positions(text, element, offset=0):
    text = text.lower()
    # print(abstract)
    element = element.lower()
    # print(element)

    if element not in text:
        return []

    index_pos_list = []

    for match in re.finditer(element, text):
        index_pos_list.append({'start': match.start() + offset, 'end': match.end() + offset})

    return index_pos_list


def create_annotation_object(id, article, concept, position):
    items = [{
        "type": "TextualBody",
        "value": concept.pref_label
    }]
    for synonym in concept.synonyms:
        items.append({
            "type": "TextualBody",
            "value": synonym
        })
    return {
        "@context": "http://www.w3.org/ns/anno.jsonld",
        "id": id,
        "type": "Annotation",
        "body": [
            {
                "type": "Choice",
                "source": concept.id,
                "items": items
            }
        ],
        "target": {
            "id": article.uri,
            "selector": {
                "type": "TextPositionSelector",
                "start": position['start'],
                "end": position['end'],
            }
        }
    }


def write_annotations_to_database(list, collection="annotation"):
    col = db[collection]
    col2 = db["annotation_to_article"]
    while len(list) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
            item = list.pop()

            future = executor.submit(col.insert_one, item[0])
            result_ = future.result()

            relationship = {"annotation_id": item[0]["id"], "pm_id": item[1]}
            future = executor.submit(col2.insert_one, relationship)
            result_ = future.result()


def write_details_into_database():
    col = db["annotated_article_ids"]
    while len(detailed_article_list) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
            future = executor.submit(col.insert_one, detailed_article_list.pop())
            result_ = future.result()


def create_detailed_article_object(article):
    return {
        "id": article.pm_id,
        "title": article.title,
        "journal_name": article.journal_name,
        "pubmed_link": article.pubmed_link,
        "author_list": article.author_list,
        "institution_list": article.instutation_list,
        "article_date": article.article_date,
        "top_three_keywords": article.top_three_keywords,
        "abstract": article.abstract,
        "article_type": article.article_type
    }


def get_annotation_counter_start():
    lastEntryIndex = -1
    query = {}
    column = db["annotation"]
    documents = column.find(query).sort("id", -1)
    if documents.count() != 0:
        lastEntryIndex = dict(documents[0])["id"]
    return lastEntryIndex + 1


def get_detailed_article_ids_from_db():
    query = {}
    column = db["annotated_article_ids"]
    document = column.find(query)
    for x in document:
        list_item = dict(x)
        if list_item["id"] not in already_inserted_detailed_article_id_list:
            already_inserted_detailed_article_id_list.append(list_item["id"])


def bulk_json_data(json_list, _index, doc_type):
    for json in json_list:
        if '{"index"' not in json:
            yield {
                "_index": _index,
                "_type": doc_type,
                "_id": uuid.uuid4(),
                "_source": json
            }


if __name__ == "__main__":
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    print("Retrieving " + str(number_of_article) + " article pubmed ids from Pubmed related to: ", search_keywords)
    # already_inserted_detailed_article_id_list
    retrieved_article_ids = []
    # get all detailed articles from db
    get_detailed_article_ids_from_db()
    for search_keyword in search_keywords:
        ids = retrieve_article_ids(search_keyword, number_of_article)
        for i in ids:
            if i not in retrieved_article_ids:
                retrieved_article_ids.append(i)

    annotated_article_ids = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        future = executor.submit(annotate, retrieved_article_ids)
        annotated_article_ids = future.result()

    try:
        elastic = Elasticsearch(hosts=["es01"])
        # print(articles)
        response = helpers.bulk(elastic, bulk_json_data(articles, "test5", "doc"))
        # print("\nRESPONSE:", response)
    except Exception as e:
        print("\nERROR:", e)

    now = datetime.now()
    finish_time = now.strftime("%H:%M:%S")
    print("start time: ", start_time)
    print("finish time: ", finish_time)
