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
DEV_DOC = os.getenv("TEST_DOCUMENT")
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/generative-language.retriever'])
generative_service_client = glm.GenerativeServiceClient(credentials=scoped_credentials)
retriever_service_client = glm.RetrieverServiceClient(credentials=scoped_credentials)
permission_service_client = glm.PermissionServiceClient(credentials=scoped_credentials)

def time_to_timestamp(timestr: Union[str, datetime]) -> float:
    if isinstance(timestr, datetime):
        return timestr.timestamp()
    elif isinstance(timestr, str):
        time_format = "%Y-%m-%d %H:%M:%S"
        try:
            parsed_time = datetime.strptime(timestr, time_format)
            return parsed_time.timestamp()
        except ValueError as e:
            raise ValueError(f"Invalid date string format: {e}")
    else:
        raise TypeError("Input must be a datetime object or a string in the format 'YYYY-MM-DD HH:MM:SS'")


class CorpusAgent:
    retriever = retriever_service_client
    generator = generative_service_client

    def __init__(self, document = None, corpus_name=CORPUS_NAME, model_name="models/aqa", ):
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
        self.current_document = create_document_response.name
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
        return
    
    def _generate_filters(self, filters: Dict[str, Union[str, float]]):
        metadata_filters = []
        min_lat = filters["min_lat"]
        min_lng = filters["min_lng"]
        max_lat = filters["max_lat"]
        max_lng = filters["max_lng"]
        current_time = filters["cur_time"]
        time_range = filters["time_range"]

        lat_filter = glm.MetadataFilter(
            key="chunk.custom_metadata.latitude",
            conditions=[
                glm.Condition(
                    numeric_value=max_lat,
                    operation=glm.Condition.Operator.LESS_EQUAL
                )
            ]
        )
        lat_filter2 = glm.MetadataFilter(
            key="chunk.custom_metadata.latitude",
            conditions=[
                
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
                )
            ]
        )
        lng_filter2 = glm.MetadataFilter(
            key="chunk.custom_metadata.longitude",
            conditions=[
                glm.Condition(
                    numeric_value=min_lng,
                    operation=glm.Condition.Operator.GREATER_EQUAL
                )
            ]
        )
        metadata_filters.append(lat_filter)
        metadata_filters.append(lng_filter)
        metadata_filters.append(lat_filter2)
        metadata_filters.append(lng_filter2)

        timestamp = time_to_timestamp(current_time)
        time_filter = glm.MetadataFilter(
            key="chunk.custom_metadata.timestamp",
            conditions=[
                glm.Condition(
                    numeric_value=(timestamp-time_range*60),
                    operation=glm.Condition.Operator.GREATER_EQUAL
                )
            ]
        )

        metadata_filters.append(time_filter)
        
        # print(metadata_filters)
        return metadata_filters


    def query_corpus(self, filters: Dict[str, Union[str, float]], query: str):
        
        metadata_filters = self._generate_filters(filters)
        request = glm.QueryCorpusRequest(name=self.corpus_name,
                                        query=query,
                                        metadata_filters=metadata_filters)
        
        query_corpus_response = self.retriever.query_corpus(request)
        if query_corpus_response == None:
            print("no response")
        
        # print(query_corpus_response.relevant_chunks)
        return query_corpus_response.relevant_chunks
    


    def generate_answer(self, filters: Dict[str, Union[str, float]], query: str, answer_style: str):
        query_content = glm.Content(parts=[glm.Part(text=query)])
        if filters == None:
            retriever_config = glm.SemanticRetrieverConfig(
                source=self.corpus_name,
                query=query_content
            )
        else:
            retriever_config = glm.SemanticRetrieverConfig(
                source=self.corpus_name,
                query=query_content,
                metadata_filters=self._generate_filters(filters)
            )
        req = glm.GenerateAnswerRequest(model=self.model_name,
                                        contents=[query_content],
                                        semantic_retriever=retriever_config,
                                        answer_style=answer_style)
        try:
            response = generative_service_client.generate_answer(req)
            response_text = ""
            # print(type(response.answer.content.parts[0].text))
            for part in response.answer.content.parts:
                response_text += part.text

            return response_text, response.answerable_probability
        except Exception as e:
            print("error occured when retrieving informatinos from corpus", e)
            response = "I'm so sorry, there are no infromations about the question."
            probability = -1
            return response, probability
    
        
    

if __name__ == "__main__":
    print(DEV_DOC)
    agent = CorpusAgent(document=DEV_DOC)
    # agent.delete_corpus()
    # agent.create_corpus()
    # agent.create_document(display_name="test document", time="2024-10-19 23:58:00")
    agent.add_info_to_document(content="there's no one at the basketball court", lat=24.787612, lng=120.994682, time="2024-10-20 11:40:00")
    agent.add_info_to_document(content="many people at the volleyball court !", lat=24.787817, lng=120.995101, time="2024-10-20 11:45:00")
    agent.add_info_to_document(content="小木屋鬆餅排超多人", lat=24.7869499, lng=120.9967584, time="2024-10-20 11:55:20")
    agent.add_info_to_document(content="long queue in front of Shinemood …", lat=24.78763954643661, lng=120.99760950557972 , time="2024-10-20 11:54:20")
    agent.add_info_to_document(content="小木屋超多人", lat=24.78743846760457, lng=120.99747941432128 , time="2024-10-20 11:56:30")
    agent.add_info_to_document(content="小木屋超多人", lat=24.78763954643661, lng=120.99753622632656 , time="2024-10-20 11:54:30")
    agent.add_info_to_document(content="小木屋超多人 放棄", lat=24.787403334838412, lng=120.99758645143267 , time="2024-10-20 11:55:30")
    agent.add_info_to_document(content=" long queue at waffle place", lat=24.787403334838412, lng=120.99758645143267 , time="2024-10-20 11:56:30")
    agent.add_info_to_document(content=" 圖書館6樓沒位置...", lat=24.7869499, lng=120.9967584 , time="2024-10-20 11:30:30")
    agent.add_info_to_document(content=" 圖書館6樓沒位置了", lat=24.7869499, lng=120.99675841 , time="2024-10-20 11:31:30")
    agent.add_info_to_document(content=" 圖書館6樓有位置了!", lat=24.7869499, lng=120.99675841 , time="2024-10-20 11:50:30")
    agent.add_info_to_document(content="麥當勞人潮排到門外了 !!!", lat=24.7854109, lng=120.9968926 , time="2024-10-20 11:50:30")
    agent.add_info_to_document(content="麥當勞人超多", lat=24.7854109, lng=120.9968925 , time="2024-10-20 11:50:15")
    agent.add_info_to_document(content="麥當勞超多人", lat=24.7854109, lng=120.9968936 , time="2024-10-20 11:50:15")
    agent.add_info_to_document(content="too many people at McDonalds ;(", lat=24.7854109, lng=120.9968926 , time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="too many people at McDonalds ;(", lat=24.7854109, lng=120.9968926 , time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="too many people at McDonalds ;(", lat=24.7854109, lng=120.9968926 , time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="我在竹湖中間!", lat=24.78834079366769, lng=120.99999957821034, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="颱風把這裡的樹吹倒了", lat=24.786519342092486, lng=121.00042873166215, time="2024-10-20 11:51:05")
    agent.add_info_to_document(content="體育館現在在舉辦黑客松", lat=24.788723995517937, lng=120.9957478164327, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="星巴克今天買一送一!!", lat=24.79726121263687, lng=120.996679810602, time="2024-10-20 11:56:15")
    agent.add_info_to_document(content="二餐有賣好吃草莓", lat=24.789688943483682, lng=120.99735011405863, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="欸欸這裡只剩下一台oloo，快點", lat=24.790876907844513, lng=120.99596979972341, time="2024-10-20 11:55:15")
    agent.add_info_to_document(content="土地公可以保佑我期中考順利嗎QQ", lat=24.78983577943657, lng=120.99995886564132, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="太棒了好久沒吃日全蒸餃，而且沒有很多人！", lat=24.798229900028737, lng=120.99676967016246, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="要怎麼走去交大體育館參加黑客松啊", lat=24.794082682458583, lng=120.9933623505233, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="路易莎今天拿鐵半價！", lat=24.79551304912013, lng=120.99554097684936, time="2024-10-20 11:52:15")
    agent.add_info_to_document(content="啊清大為什麼又停電了", lat=24.79209385712424, lng=120.99363459150261, time="2024-10-20 11:40:15")
    agent.add_info_to_document(content="宿舍好黑...", lat=24.790694871701678, lng=120.99455631324706, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="又停電...還我冷氣！！", lat=24.790694871701678, lng=120.99455631324706, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="這學期是要停電幾次嗚嗚嗚", lat=24.791132873507166, lng=120.99372100291617, time="2024-10-20 11:50:15")
    agent.add_info_to_document(content="今天健身房也太多人了吧...", lat=24.789746952051434, lng=120.9956292549652, time="2024-10-20 11:51:15")
    agent.add_info_to_document(content="這個天氣游泳很舒服～～", lat=24.789733877247002, lng=120.99617652725097, time="2024-10-20 11:51:15")


    
    
    
    # filters = {
    #     "min_lat":24.0,
    #     "max_lat":31.0,
    #     "min_lng":115.0,
    #     "max_lng":125.0,
    #     "cur_time": "2024-10-19 00:00:00",
    #     "time_range": 60
    # }


    # agent.query_corpus(filters=filters, query="Give me traffic info")

    # try:
    #     agent.generate_answer(filters=None, query=query, answer_style="ABSTRACTIVE")
    # except Exception as e:
    #     print(e)
    # get_document_request = glm.GetDocumentRequest(name="corpora/gemihubcorpus-vviogw42kc9t/documents/test-document-3-hknhyc3kwtsx")

    # # Make the request
    # # document_resource_name is a variable set in the "Create a document" section.
    # get_document_response = retriever_service_client.get_document(get_document_request)

    # # Print the response
    # print(get_document_response)
    # get_corpus_request = glm.GetCorpusRequest(name=CORPUS_NAME)

    # # Make the request
    # get_corpus_response = retriever_service_client.get_corpus(get_corpus_request)

    # # Print the response
    # print(get_corpus_response)
    # req = glm.DeleteDocumentRequest(name="corpora/gemihubcorpus-7vin6z0kps/documents/test-document-k9jy58yju3kq", force=True)
    # delete_doc_response = retriever_service_client.delete_document(req)
    # print(delete_doc_response)
