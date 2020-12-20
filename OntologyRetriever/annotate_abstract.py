#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[2]:


import ontology_retriever as onRe

print("Retrieving all concepts in the following list of ontologies: ", onRe.list_of_bioportal_ontologies)
concepts = onRe.retrieve_annotations("dde26f65-ec2b-49b4-b3e7-090e5da33350", max_page_limit=10)  


# In[3]:


import requests
import xmltodict

search_keyword="bipolar"
number_of_article=3

class Article:
    pmid = ""
    title = ""
    abstract = ""
    journal_issn = ""
    journal_name = ""

    def __init__(self, pmid, title,journal_issn, journal_name):
        self.pmid = pmid
        self.title = title
        self.journal_issn = journal_issn
        self.journal_name = journal_name


class EntrezSearchRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    searchTerm = ""
    max_article_limit = 20

    def __init__(self, searchTerm, max_article_limit):
        self.searchTerm = searchTerm
        self.max_article_limit = max_article_limit

    def __str__(self):
        return self.base_url + "esearch.fcgi?db=pubmed&term=" + self.searchTerm + "&retmax=" + str(
            self.max_article_limit)


class EntrezGetAbstractRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    id = 0

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.base_url + "efetch.fcgi?db=pubmed&id=" + self.id + "&retmode=text&rettype=abstract"


class EntrezGetArticleRequest:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    id = 0

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return self.base_url + "efetch.fcgi?db=pubmed&id=" + self.id + "&retmode=xml"


def retrieve_article_ids(search_term, max_article_limit):
    response = requests.get(EntrezSearchRequest(search_term, max_article_limit))

    if response.ok:
        xpars = xmltodict.parse(response.text)
        article_count = xpars['eSearchResult']['Count']
        returned_article_id_count = int(xpars['eSearchResult']['RetMax'])
        print("From " + article_count + " articles " + str(returned_article_id_count) + " article ids are retrieved")
        article_id_list = xpars['eSearchResult']['IdList']
        ''' 
        for id in range(0, int(returned_article_id_count)):
            print("\t"+xpars['eSearchResult']['IdList']['Id'][id])  
        '''
        return xpars['eSearchResult']['IdList']['Id']
    else:
        print("\tThis article id could not be retrieved.")


def get_abstract_of_given_article_id(id):
    response = requests.get(EntrezGetAbstractRequest(id))

    if response.ok:
        return response.text
    else:
        print("\tThis article abstract could not be retrieve for given id.")


def retrieve_articles(id):
    response = requests.get(EntrezGetArticleRequest(id))

    if response.ok:
        xpars = xmltodict.parse(response.text)
        article = xpars["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
        article_title = article["ArticleTitle"]
        journal_issn = article["Journal"]["ISSN"]["#text"]
        journal_name = article["Journal"]["Title"]

        return Article(id, article_title, journal_issn, journal_name)
    else:
        print("\tArticle could not be retrieved.")


# In[4]:


if __name__ == "__main__":

    print("Retrieving " + str(number_of_article) + " article pubmed ids from Pubmed related to: ", search_keyword)
    retrieved_article_ids = retrieve_article_ids(search_keyword, number_of_article)

    if len(retrieved_article_ids) > 0:
        for id in range(0, len(retrieved_article_ids)):
            print("Retrieving articles with pubmed id=" + str(retrieved_article_ids[id]))
            article = retrieve_articles(retrieved_article_ids[id])
            article.abstract=get_abstract_of_given_article_id(retrieved_article_ids[id])
            for c in concepts:
                if (c.pref_label in article.abstract):
                    print(
                        "Article with id: " + retrieved_article_ids[id] + " has ontolgy concept: " + c.id + " (synonyms=" + c.pref_label + ")")
                


# In[5]:


response=requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="+str(33307467)+"&retmode=xml")
xpars = xmltodict.parse(response.text)
article = xpars["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
article


# In[6]:


article["Abstract"]["AbstractText"]


# In[ ]:




