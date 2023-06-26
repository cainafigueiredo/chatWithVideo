import re
from typing import Text
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS

def initChatBot(llm):
    CHATBOT_TEMPLATE = """You are an advanced chatbot equipped to assist users in extracting valuable information from video transcripts. Your primary objective is to provide accurate answers based on the available context, timestamps, and user input. When generating your response, focus on the relevant snippets of the context rather than the entire transcript. Use the following format to provide your answer:
    - Based on video clip from <start timestamp 1> to <end timestamp 1>: <your answer>.
    - Based on video clip from <start timestamp 2> to <end timestamp 2>: <your answer>.
    ...
    - Based on video clip from <start timestamp n> to <end timestamp n>: <your answer>.""

    Transcripts: {context}

    User's input: {query}

    Answer: """

    chatBotPrompt = PromptTemplate(template = CHATBOT_TEMPLATE, input_variables = ["context", "query"])

    chatbot = LLMChain(
        prompt = chatBotPrompt,
        llm = llm
    )

    return chatbot

def getRetriever(transcripts, videoURL, splitter, embeddings):
    transcriptDocuments = splitter.create_documents([transcripts], metadatas = [{"url": videoURL}])
    vectorstore = FAISS.from_documents(transcriptDocuments, embedding = embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

def cleanText(text: Text):
    text = text.strip()
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"\n", "", text)
    return text