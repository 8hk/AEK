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

client = MongoClient(
    host=os.environ.get("MONGO_DB_HOST", " ") + ":" + os.environ.get("MONGO_DB_PORT", " "),  # <-- IP and port go here
    serverSelectionTimeoutMS=3000,  # 3 second timeout
    username=os.environ.get("MONGO_DB_USERNAME", " "),
    password=os.environ.get("MONGO_DB_PASSWORD", " "),
)

db = client[os.environ.get("MONGO_INITDB_DATABASE", " ")]

# import ontology_retriever as onRe
# print("Retrieving all concepts in the following list of ontologies: ", onRe.list_of_bioportal_ontologies)
# concepts = onRe.retrieve_annotations(API_KEY, max_page_limit=10)
infile = open('concepts', 'rb')
concepts = pickle.load(infile)
infile.close()

search_keyword = "bipolar disorder"
number_of_article = 3


class Article:
    pm_id = ""
    title = ""
    abstract = ""
    journal_issn = ""
    journal_name = ""
    pubmed_link = ""

    def __init__(self, pm_id, title, journal_issn, journal_name, abstract, pubmed_link):
        self.pm_id = pm_id
        self.title = title
        self.journal_issn = journal_issn
        self.journal_name = journal_name
        self.abstract = abstract
        self.pubmed_link = pubmed_link


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
    response = requests.get(EntrezSearchRequest(search_term, max_article_limit))

    if response.ok:
        xpars = xmltodict.parse(response.text)
        article_count = xpars['eSearchResult']['Count']
        returned_article_id_count = int(xpars['eSearchResult']['RetMax'])
        print("From " + article_count + " articles " + str(returned_article_id_count) + " article ids are retrieved")
        return xpars['eSearchResult']['IdList']['Id']
    else:
        print("\tThis article id could not be retrieved.")


def get_abstract_of_given_article_id(article_id):
    response = requests.get(EntrezGetAbstractRequest(article_id))

    if response.ok:
        return response.text
    else:
        print("\tThis article abstract could not be retrieve for given id.")


def retrieve_article(article_id):
    response = requests.get(EntrezGetArticleRequest(article_id))
    if response.ok:
        xpars = xmltodict.parse(response.text)
        article = xpars["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
        article_title = article["ArticleTitle"]
        journal_issn = article["Journal"]["ISSN"]["#text"]
        journal_name = article["Journal"]["Title"]
        pubmed_link = "https://pubmed.ncbi.nlm.nih.gov/" + str(article_id) + "/"
        abstract = article["Abstract"]["AbstractText"]

        return Article(article_id, article_title, journal_issn, journal_name, abstract, pubmed_link)
    else:
        print("\tArticle could not be retrieved.")


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
    annotation_list = []
    annotation_counter = 0
    if len(retrieved_article_ids) > 0:
        for id in range(0, len(retrieved_article_ids)):
            print("Retrieving articles with pubmed id=" + str(retrieved_article_ids[id]))
            article = retrieve_article(retrieved_article_ids[id])
            article.abstract = get_abstract_text(article.abstract)
            # print(str(id)+"\n")
            # print(article.abstract)
            for c in concepts:
                positions = get_index_positions(article.abstract, c.pref_label)
                if positions != []:
                    for position in positions:
                        print("ONTOLOGY CONCEPT: " + c.pref_label + " POSITION START:" + str(
                            position['start']) + " POSITION END:" + str(position['end']) + "\n")
                        # print("Article with id: " + retrieved_article_ids[id] + " has ontolgy concept: " + c.id + " (synonyms=" + c.pref_label + ")")
                        annotation_object = create_annotation_object(annotation_counter, article, c, position)
                        print(annotation_object)
                        annotation_counter = annotation_counter + 1
                        annotation_list.append(annotation_object)
                    print("\n--------------------------------------------")
    return annotation_list


def get_index_positions(abstract, element):
    abstract = abstract.lower()
    # print(abstract)
    element = element.lower()
    # print(element)

    if element not in abstract:
        return []

    index_pos_list = []

    for match in re.finditer(element, abstract):
        index_pos_list.append({'start': match.start(), 'end': match.end()})

    return index_pos_list


def create_annotation_object(id, article, concept, position):
    return {
        "@context": "http://www.w3.org/ns/anno.jsonld",
        "id": id,
        "@type": "Annotation",
        "body": [
            {
                "type": "TextualBody",
                "source": concept.id,
                "value": concept.synonyms
            }
        ],
        "target": {
            "id": article.pm_id,
            "selector": {
                "type": "TextPositionSelector",
                "start": position['start'],
                "end": position['end'],
            }
        }
    }


def write_annotation_to_database(annotation_list):
    for annotation in annotation_list:
        print(annotation)
        db.annotation.insert_one(annotation)


if __name__ == "__main__":
    print("Retrieving " + str(number_of_article) + " article pubmed ids from Pubmed related to: ", search_keyword)

    retrieved_article_ids = retrieve_article_ids(search_keyword, number_of_article)

    annotation_list = annotate(retrieved_article_ids)

    write_annotation_to_database(annotation_list)
