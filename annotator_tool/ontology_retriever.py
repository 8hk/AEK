#############################################################################################################
#                                                                                                           #
#   Retrieves concepts with their labels, ids and synonyms from BioPortal for a given list of ontologies.   #
#                                                                                                           #
#   BioPortal REST API:                                                                                     #
#   http://data.bioontology.org/ontologies/ONTOLOGY_ACRONYM/classes?apikey=API_KEY                          #
#                                                                                                           #
#   Example:                                                                                                #
#   http://data.bioontology.org/ontologies/MFOMD/classes?apikey=API_KEY                                     #
#                                                                                                           #
#############################################################################################################

import requests

list_of_bioportal_ontologies = [

    # MFO Mental Disease Ontology (MFOMD)
    "MFOMD",

    # EDAM Bioimaging Ontology (EDAM-BIOIMAGING)
    "EDAM-BIOIMAGING",

    # International Classification of Functioning, Disability and Health (ICF)
    "ICF",

    # Symptom Ontology (SYMP)
    "SYMP",

    # Gender, Sex, and Sexual Orientation Ontology (GSSO)
    "GSSO",

    # Environment Ontology (ENVO)
    "ENVO",

    ### Too many entries:

    # Mondo Disease Ontology (MONDO)
    "MONDO",

    # SNOMED CT (SNOMEDCT)
    "SNOMEDCT",

    # Human Disease Ontology (DOID)
    "DOID",

    # Medical Subject Headings (MESH)
    "MESH",

    # Read Codes, Clinical Terms Version 3 (CTV3) (RCD)
    "RCD",

    # National Drug Data File (NDDF)
    "NDDF",

    # Few synonyms:
    # Biological Imaging Methods Ontology (FBbi)
    # Cognitive Atlas Ontology (COGAT)

    # Very few synonyms:
    # The Drug Ontology (DRON)
    # Psychology Ontology (APAONTO)
    # Quantities, Units, Dimensions, and Types Ontology (QUDT)
    # Ontology for General Medical Science (OGMS)
    # Autism Spectrum Disorder Phenotype Ontology (ASDPTO)
    # PatientSafetyOntology (PSO)
    # Medical Web Lifestyle Aggregator (MWLA)
    # Heart Failure Ontology (HFO)
    # Drug Interaction Knowledge Base Ontology (DIKB)

]

class Concept:
    pref_label = ""
    id = ""
    synonyms = []

    def __init__(self, pref_label, id, synonyms = []):
        self.pref_label = pref_label
        self.id = id
        self.synonyms = synonyms

class BioportalOntologyRequest:
    base_url = "http://data.bioontology.org/ontologies/"
    api_key = ""
    ontology = ""
    page = 0

    def __init__(self, ontology, api_key, page):
        self.ontology = ontology
        self.api_key = api_key
        self.page = page

    def __str__(self):
        return self.base_url + self.ontology + "/classes?apikey=" + self.api_key +"&page=" + str(self.page)

def retrieve_annotations(api_key, max_page_limit=0):

    if api_key == "":
        print("Please pass an API key for BioPortal.")

    list_of_concepts = []

    for ontology in list_of_bioportal_ontologies:
        page_count = 1
        page = 1
        print("Ontology:", ontology)
        while page <= (min(page_count, max_page_limit) if max_page_limit > 0 else page_count):
            response = requests.get(BioportalOntologyRequest(ontology, api_key, page))

            if response.ok:
                json = response.json()
                page_count = int(json["pageCount"])
                num_of_classes = len(json["collection"])
                print("\tPage: ", page, "/", page_count)
                print("\t\tNumber of classes in this page: ", num_of_classes)
                for concept in range(0, num_of_classes):
                    pref_label = json["collection"][concept]["prefLabel"]
                    id = json["collection"][concept]["@id"]
                    synonyms = json["collection"][concept]["synonym"]
                    list_of_concepts.append(Concept(pref_label, id, synonyms))
            else:
                print("\tThis ontology could not be retrieved.")

            page += 1

    return list_of_concepts

if __name__ == "__main__":
    print("Retrieving all concepts in the following list of ontologies: ", list_of_bioportal_ontologies)
    concepts = retrieve_annotations(API_KEY, max_page_limit=10)

    for c in concepts:
        print(c.pref_label, c.id, c.synonyms)