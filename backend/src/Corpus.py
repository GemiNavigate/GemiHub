import google.ai.generativelanguage as glm
from google.oauth2 import service_account
from dotenv import load_dotenv
import os
from typing import Dict, List, Optional, Union
from datetime import datetime
from geopy.distance import distance
from geopy.point import Point

load_dotenv()
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
CORPUS_NAME=os.getenv("CORPUS_NAME")
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])
generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)


def time_to_timestamp(timestr):
    time_format = "%Y-%m-%d %H:%M:%S"
    timestamp = datetime.strptime(timestr, time_format).timestamp()
    return timestamp

def get_bounding_box(center_lat, center_lon, distance_km):
    # Define the central point as a geopy Point object
    center_point = Point(center_lat, center_lon)

    # Calculate points in the four cardinal directions (north, south, east, west)
    north_point = distance(kilometers=distance_km).destination(center_point, 0)   # 0 degrees -> north
    south_point = distance(kilometers=distance_km).destination(center_point, 180) # 180 degrees -> south
    east_point = distance(kilometers=distance_km).destination(center_point, 90)   # 90 degrees -> east
    west_point = distance(kilometers=distance_km).destination(center_point, 270)  # 270 degrees -> west

    # Bounding box coordinates
    min_lat = south_point.latitude
    max_lat = north_point.latitude
    min_lng = west_point.longitude
    max_lng = east_point.longitude

    return (min_lat, max_lat, min_lng, max_lng)

class CorpusAgent:
    retriever = retriever_service_client
    generator = generative_service_client

    def __init__(self, document, corpus_name=CORPUS_NAME, model_name="models/aqa", ):
        self.corpus_name = corpus_name
        self.model_name = model_name
        self.current_document = document
        return

    def create_corpus(self):
        #Don't call if you already have a corpus
        corpus = glm.Corpus(display_name="gemihub_corpus")
        create_corpus_request = glm.CreateCorpusRequest(corpus=corpus)
        create_corpus_response = self.retriever.create_corpus(create_corpus_request)
        print(create_corpus_response)
        self.corpus_name = create_corpus_response.name
        return self.corpus_name
    
    def delete_corpus(self):
        # Set force to False if you don't want to delete non-empty corpora.
        req = glm.DeleteCorpusRequest(name=self.corpus_name, force=True)
        delete_corpus_response = retriever_service_client.delete_corpus(req)
        print(delete_corpus_response)
        return

    def create_document(self, display_name: str, time: str):
        # create new document every hour(?)
        # display_name is the string content
        document = glm.Document(display_name=display_name)
        # Add metadata.
        timestamp = time_to_timestamp(time)
        document_metadata = [
            glm.CustomMetadata(key="EoL", numeric_value=timestamp+86400)
        ]
        
        document.custom_metadata.extend(document_metadata)

        create_document_request = glm.CreateDocumentRequest(parent=self.corpus_name, document=document)
        create_document_response = self.retriever.create_document(create_document_request)
        print(create_document_response)

        return create_document_response.name
    
    def add_info_to_document(self, content: str, lat: float, lng: float, time: str):
        timestamp = time_to_timestamp(time)
        chunk = glm.Chunk(data={'string_value': content})
        chunk.custom_metadata.append(glm.CustomMetadata(key="latitude", numeric_value=lat))
        chunk.custom_metadata.append(glm.CustomMetadata(key="longitude", numeric_value=lng))
        chunk.custom_metadata.append(glm.CustomMetadata(key="timestamp", numeric_value=timestamp))

        create_chunk_request = glm.CreateChunkRequest(parent=self.current_document, chunk=chunk)
        response = self.retriever.create_chunk(create_chunk_request)
        print(response)
        return
    
    def _generate_filters(self, filters: Dict[str, Dict]):
        metadata_filters = []
        for key, condition in filters.items():
            if key=="location":
                lat = condition["lat"]
                lng = condition["lng"]
                dst = condition["dst"]
                min_lat, max_lat, min_lng, max_lng = get_bounding_box(lat, lng, dst)
                lat_filter = glm.MetadataFilter(
                    key="chunk.custom_metadata.latitude",
                    conditions=[
                        glm.Condition(
                            numeric_value=max_lat,
                            operation=glm.Condition.Operator.LESS_EQUAL
                        ),
                        glm.Condition(
                            numeric_value=min_lat,
                            operation=glm.Condition.Operator.GREATER_EQUAL
                        )
                    ]
                )
                lng_filter = glm.MetadataFilter(
                    key="chunk.custom_metadata.longitude",
                    conditions=[
                        glm.Condition(
                            numeric_value=max_lng,
                            operation=glm.Condition.Operator.LESS_EQUAL
                        ),
                        glm.Condition(
                            numeric_value=min_lng,
                            operation=glm.Condition.Operator.GREATER_EQUAL
                        )
                    ]
                )

                metadata_filters.append(lat_filter)
                metadata_filters.append(lng_filter)

            elif key=="timestamp":
                current_time = condition['current_time']
                timestamp = time_to_timestamp(current_time)
                time_range = condition['range']
                time_filter = glm.MetadataFilter(
                    key="chunk.custom_metadata.timestamp",
                    conditions=[
                        glm.Condition(
                            numeric_value=(timestamp-time_range),
                            operation=glm.Condition.Operator.GREATER_EQUAL
                        )
                    ]
                )

                metadata_filters.append(time_filter)
        
        # print(metadata_filters)
            
        return metadata_filters


    def query_corpus(self, filters: Dict[str, Dict], query: str):
        # filter format
        # {
        #     location: {
        #       lat:
        #       lng:
        #       dst:
        #     },
        #     timestamp: {
        #       current_time:
        #       range: 
        #     }
        # }
        metadata_filters = self._generate_filters(filters)
        request = glm.QueryCorpusRequest(name=self.corpus_name,
                                        query=query,
                                        metadata_filters=metadata_filters)
        
        query_corpus_response = self.retriever.query_corpus(request)
        if query_corpus_response == None:
            print("no response")
        
        print(query_corpus_response)
        return query_corpus_response
    


    def generate_answer(self, filters: Dict[str, Dict], query: str, answer_style: str):
        query_content = glm.Content(parts=[glm.Part(text=query)])
        
        retriever_config = glm.SemanticRetrieverConfig(
            source=self.corpus_name,
            query=query_content,
            metadata_filters=self._generate_filters(filters)
        )
        req = glm.GenerateAnswerRequest(model=self.model_name,
                                        contents=[query_content],
                                        semantic_retriever=retriever_config,
                                        answer_style=answer_style)
        response = generative_service_client.generate_answer(req)
        print("response: ")
        print(response)
        return response
    

if __name__ == "__main__":
    agent = CorpusAgent(document="corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-3-hknhyc3kwtsx")
    # agent.delete_corpus()
    # agent.create_corpus()
    # agent.create_document(display_name="test document 3", time="2024-10-16 09:46:00")
    # filters = {}
    # agent.add_info_to_document(content="I saw a traffic accident", lat=12.36, lng=112.65, time="2024-10-16 09:46:31")
    # filters = {
    #     "location": {
    #         "lat":12.36,
    #         "lng":112.65,
    #         "dst":5.0
    #     },
    #     "timestamp": {
    #         "current_time": "2024-10-16 09:47:00",
    #         "range": 60
    #     }
    # }
    # # agent.query_corpus(filters=filters, query="Is the first chunk still in the document?")
    # agent.generate_answer(filters=filters, query="Are there any traffic accidents?", answer_style="VERBOSE")
    # get_document_request = glm.GetDocumentRequest(name="corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-1-krzt9f21eiah")

    # # Make the request
    # # document_resource_name is a variable set in the "Create a document" section.
    # get_document_response = retriever_service_client.get_document(get_document_request)

    # # Print the response
    # print(get_document_response)
    