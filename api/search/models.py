# from django.db import models
from djongo import models

class AnnotatedArticle(models.Model):
    body_value = models.CharField(max_length=255)
    target = models.CharField(max_length=255,null=True)


    def __str__(self):
        return str(self.body_value)

    @property
    def sd(self):
        return{
            "@type": 'Annotation',
            "body": {
            "type": "TextualBody",
            "value": self.body_value
            }
        }

#
#     """
#     {
#     "@context": "http://www.w3.org/ns/anno.jsonld",
#       "id": "<annotation id (incremental)>",
#       "type": "Annotation",
#       "body":
#         {
#           "type": "TextualBody",
#           "source": "<ontology + concept id>" // ontology 1
#           "value": <synonym>
#         }
#
#       "target": {
#         "id": "<article id>",
#         "selector": {
#           "type": "TextPositionSelector",
#           "start": <start position in article>,
#           "end": <end position in article>
#         }
#
#       }
#     }
#     """