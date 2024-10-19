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


def time_to_timestamp(timestr):
    time_format = "%Y-%m-%d %H:%M:%S"
    timestamp = datetime.strptime(timestr, time_format).timestamp()
    return timestamp

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
        print(response)
        return
    
    def _generate_filters(self, filters: Dict[str, Union[str, float]]):
        metadata_filters = []
        min_lat = filters["min_lat"]
        min_lng = filters["min_lng"]
        max_lat = filters["max_lat"]
        max_lng = filters["max_lng"]
        current_time = filters["current_time"]
        time_range = filters["time_range"]
        
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
        
        print("\n\nfilter:\n") 
        print(metadata_filters)
        print("\n\n")
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
        print("req success")
        try:
            response = generative_service_client.generate_answer(req)
            print("original response from corpus")
            print(response)
            print("end!!!\n\n")
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
    # agent.create_document(display_name="test document", time="2024-10-19 10:46:00")
    content = '''
location: (30.0988, 121.98765)
Information: No accidents acutally happened
'''
    # agent.add_info_to_document(content=content, lat=30.0988, lng=121.98765, time="2024-10-19 10:00:00")
    agent.add_info_to_document(content="清大客運站爆多人，要遲到了:(", lat=24.795523820, lng=120.998332165, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="這裡有很多仙草蜜", lat=24.78979280059065, lng=120.99996938779464, time="2024-10-20 11:45:00")
    agent.add_info_to_document(content="小心工六這邊剛剛火災了！", lat=24.786009923950427, lng=120.99734198471171, time="2024-10-20 11:52:00")
    agent.add_info_to_document(content="Engineering building V is on fire! Be careful if you have to pass through here.", lat=24.786009923950427, lng=120.99734198471171, time="2024-10-20 12:00:00")
    agent.add_info_to_document(content="Help! a car just hit a pedestrian!", lat=24.795931608762007, lng=120.99790046557531, time="2024-10-20 11:57:00")
    agent.add_info_to_document(content="There are so many people in the badminton hall", lat=24.78743081211189, lng=121.00154734974369, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="排球場要滿了", lat=24.78785141965718, lng=120.99511917943207, time="2024-10-20 11:50:00")
    agent.add_info_to_document(content="作業要寫不完了.... 快要暴斃嗚嗚嗚", lat=24.78375794639863, lng=120.99807266308567, time="2024-10-20 11:51:00")
    agent.add_info_to_document(content="今天研三有賣手工餅乾，到下午六點要買要快！", lat=24.783923190127197, lng=120.99670760761394, time="2024-10-20 11:49:00")
    agent.add_info_to_document(content="成功湖中間，簽:)", lat=24.793521971397826, lng=120.99550801345022, time="2024-10-20 11:48:00")
    agent.add_info_to_document(content="有人在竹湖偷談戀愛 :0", lat=24.788241982508584, lng=120.99975209502698, time="2024-10-20 11:47:00")
    agent.add_info_to_document(content="I found an Iphone 16 pro max here, I put it in the flower bed nearby.", lat=24.790555291230152, lng=120.9959547589073, time="2024-10-20 11:46:00")
    agent.add_info_to_document(content="I found a student ID card here, the owner of this card is Bill.", lat=24.788279536582422, lng=120.99879241964695, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="比爾同學你的學生證掉了，我幫你把學生證放在樓梯角", lat=24.788279536582422, lng=120.99879241964695, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="Google的題目好好玩", lat=24.78880070020733, lng=120.99571630047818, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="Gemini 可以乖一點嗎", lat=24.788723386750387, lng=120.99564388083809, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="梅竹黑克松黑客組設備測試要結束囉", lat=24.788754433892432, lng=120.99587522135512, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="Google的題目怎麼這麼難", lat=24.788723995517937, lng=120.9957478164327, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="誒有電腦燒起來了", lat=24.78871303770131, lng=120.9957102655082, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="something’s burning", lat=24.78876539170542, lng=120.99567070292701, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="something smells burnt", lat=24.7887812196558, lng=120.99577463852161, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="不覺得有燒焦味嗎", lat=24.788633289117712, lng=120.99591076062293, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="體育館怎麼在冒煙", lat=24.788665553818, lng=120.99564522194252, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="Gemini 怎麼這麼難搞", lat=24.788663118746584, lng=120.9955748139591, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="電腦燒起來了", lat=24.78885001033977, lng=120.99563114034585, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="computer’s burning!", lat=24.788745302380864, lng=120.99572837041822, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="something smells like burnt plastic", lat=24.78857789121649, lng=120.99563784586806, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="the gym’s empty", lat=24.788568405136, lng=120.99565974905781, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="the lat pulldown machine is broken", lat=24.788601887389486, lng=120.99562085702887, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="這裡有遺失的錢包", lat=24.788749817965027, lng=120.99565371408781, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="Computer burning at table 2", lat=24.78875468810445, lng=120.99563024476001, time="2024-10-20 11:55:00")
    agent.add_info_to_document(content="第二桌電腦起火大家小心", lat=24.788801563186517, lng=120.99566243126671, time="2024-10-20 11:55:00")


    # filters = {
    #     "min_lat":24.0,
    #     "max_lat":31.0,
    #     "min_lng":115.0,
    #     "max_lng":125.0,
    #     "current_time": "2024-10-19 00:00:00",
    #     "time_range": 60
    # }


    # agent.query_corpus(filters=filters, query="What is the color of spongebob's pants?")
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