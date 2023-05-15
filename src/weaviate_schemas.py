
openai_schema = {
    "classes": [
        {
            "class": "Paragraph",
            "description": "A written paragraph",
            "vectorizer": "text2vec-transformers",
              "moduleConfig": {
                "text2vec-openai": {
                  "model": "ada",
                  "modelVersion": "002",
                  "type": "text"
                }
              },
            "properties": [
                {
                    "dataType": ["text"],
                    "description": "The content of the paragraph",
                    "moduleConfig": {
                        "text2vec-transformers": {
                          "skip": False,
                          "vectorizePropertyName": False
                        }
                      },
                    "name": "content",
                },
            ],
        },
    ]
}

text2vec_schema = {
  "classes": [
    {
      "class": "Document",
      "description": "A class called document",
      "moduleConfig": {
        "text2vec-transformers": {
          "poolingStrategy": "masked_mean",
          "vectorizeClassName": False
        }
      },
      "properties": [
        {
          "dataType": [
            "text"
          ],
          "description": "Content that will be vectorized",
          "moduleConfig": {
            "text2vec-transformers": {
              "skip": False,
              "vectorizePropertyName": False
            }
          },
          "name": "content"
        }
      ],
      "vectorizer": "text2vec-transformers"
    }
  ]
}

from typing import List

import numpy as np
from pydantic import BaseModel
import requests
from langchain.embeddings.base import Embeddings



class WeaviateEmbeddings(Embeddings, BaseModel):

    pooling_strategy: str
    embed_url = 'http://localhost:8081/vectors'
        

    def _get_embedding(self, text: str) -> List[float]:
        print(text)
        qry = dict(
            config = {'pooling_strategy': self.pooling_strategy
            },
            text = text
        )
        url = self.embed_url

        r = requests.post(url, json = qry)
        your_list = r.json()['vector']
        return your_list

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self._get_embedding(doc) for doc in documents]

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)
    

from weaviate.util import get_valid_uuid
from uuid import uuid4


import weaviate
import json

  
def make_weaviate_schema(index_name, text_fields_to_embed, other_text_fields, int_fields):

  index_properties = []
  for field_name in text_fields_to_embed:
    index_properties.append(
      {
          "name": field_name,
          "dataType": ["text"],
          "description": "",
          "moduleConfig": {
          "text2vec-transformers": {
              "skip": False,
              "vectorizePropertyName": False,
              "vectorizeClassName": False
          }
          }
      }
    )
  for field_name in other_text_fields:
    index_properties.append(
      {
          "name": field_name,
          "dataType": ["text"],
          "description": "",
          "moduleConfig": {
          "text2vec-transformers": {
              "skip": True,
              "vectorizePropertyName": False,
              "vectorizeClassName": False
          }
          }
      }
    )
  for field_name in int_fields:
    index_properties.append(
      {
          "name": field_name,
          "dataType": ["int"],
          "description": "",
          "moduleConfig": {
          "text2vec-transformers": {
              "skip": True,
              "vectorizePropertyName": False,
              "vectorizeClassName": False
          }
          }
      }
    )

  class_definition = {
    "class": index_name,
    "description": "",
    "moduleConfig": {
      "text2vec-transformers": {
        "poolingStrategy": "masked_mean",
        "vectorizeClassName": False
      }
    },
    'properties': index_properties
    }
  return {
     'classes': [class_definition]
  }


class WeaviateIndexOps():
  def __init__(self,
    text_fields_to_embed: list,
    index_name: str,
    other_text_fields = [],
    int_fields = [],
    db_url = "http://localhost:8080"
  ):
    self.text_fields_to_embed = text_fields_to_embed
    self.other_text_fields = other_text_fields
    self.int_fields = int_fields
    self.index_name = index_name
    self.db_url = db_url

    self.client = weaviate.Client(self.db_url,     
          #additional_headers={
          #    "X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]
          #}
                              )
    self.index_schema = make_weaviate_schema(self.index_name, self.text_fields_to_embed, self.other_text_fields, self.int_fields)
    self.all_index_properties = self.text_fields_to_embed + self.other_text_fields + self.int_fields

  def initialize_index(self, reset_index = True):
    if reset_index:
      self.client.schema.delete_all()
    self.client.schema.get()
    
    self.client.schema.create(self.index_schema)

  def add_record(self, data_dict: dict):
    id = get_valid_uuid(uuid4())
    self.client.data_object.create(
            data_object = data_dict,
            class_name = self.index_name,
            uuid=id
        )
  def add_ls_records(self, ls_dict):
    for d in ls_dict:
      self.add_record(d)

  def get_first_item(self):
    get_first_object_weaviate_query = """
    {
      Get {""" \
        + self.index_name + \
    """  {
          _additional {
            id
          }
        }
      }
    }
    """

    results = self.client.query.raw(get_first_object_weaviate_query)
    uuid_cursor = results["data"]["Get"][self.index_name][0]["_additional"]["id"]
    return uuid_cursor
  
  def get_number_records(self):
    total_objs_query = """
    {
        Aggregate {""" \
          + self.index_name + \
    """ {
                meta {
                    count
                }
            }
        }
    }
    """

    results = self.client.query.raw(total_objs_query)
    total_objects = results["data"]["Aggregate"][self.index_name][0]["meta"]["count"]

    return total_objects


  def get_all_data(self, increment = 50, include_vector_and_id = False):
    #uuid_cursor = self.get_first_item()
    total_objects = self.get_number_records()

    data = []
    for i in range(0, total_objects, increment):
        if i == 0:
          results = (
              self.client.query.get(self.index_name, self.all_index_properties)
              .with_additional(["id", "vector"])
              .with_limit(increment)
              .do()
          )["data"]["Get"][self.index_name]
          if len(results):
            result = results[0]
            uuid_cursor = result["_additional"]["id"]
        else:
          results = (
              self.client.query.get(self.index_name, self.all_index_properties)
              .with_additional(["id", "vector"])
              .with_limit(50)
              .with_after(uuid_cursor)
              .do()
          )["data"]["Get"][self.index_name]

        # extract data from result into JSON
        for result in results:
            new_obj = {}
            for key in result.keys():
                if (key == "_additional"):
                    if include_vector_and_id:
                        new_obj["_additional"] = {}
                        for additionalKey in result[key].keys():
                            new_obj["_additional"][additionalKey] = result[key][additionalKey]
                else:
                  new_obj[key] = result[key]
            data.append(new_obj)
            # update uuid cursor to continue the loop
            # we have just exited a loop where result holds the last obj
            uuid_cursor = result["_additional"]["id"]
    return data