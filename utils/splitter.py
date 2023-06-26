import re
import webvtt
from copy import copy
from io import StringIO
from typing import Any, Optional, List
from datetime import datetime, timedelta
from langchain.text_splitter import TextSplitter
from langchain.docstore.document import Document

class WebVTTTextSplitter(TextSplitter):
    def __init__(self, **kwargs: Any):
        """Create a new TextSplitter."""
        kwargs["chunk_size"] = kwargs.get("chunk_size", 30)
        kwargs["chunk_overlap"] = kwargs.get("chunk_overlap", 5)
        kwargs["length_function"] = kwargs.get("length_function", self._length_function)
        super().__init__(**kwargs)
        self.timestampPattern = r"((?:\d+:)+\d+\.\d+) --> ((?:\d+:)+\d+\.\d+)"

    def _length_function(self, text: str):
        try:
            allTimestamps = re.findall(self.timestampPattern, text)

            startTimestamp = datetime.strptime(allTimestamps[0][0], "%H:%M:%S.%f").time()
            startTimestamp = timedelta(
                hours=startTimestamp.hour, 
                minutes=startTimestamp.minute, 
                seconds=startTimestamp.second, 
                microseconds=startTimestamp.microsecond
            )

            endTimestamp = datetime.strptime(allTimestamps[-1][1], "%H:%M:%S.%f").time()
            endTimestamp = timedelta(
                hours=endTimestamp.hour, 
                minutes=endTimestamp.minute, 
                seconds=endTimestamp.second, 
                microseconds=endTimestamp.microsecond
            )
            
            totalSeconds = (endTimestamp - startTimestamp).total_seconds()
            return totalSeconds
        except: 
            # This is needed because self._merge_splits calls this method passing a separator.
            # The separator does not contribute to chunk_size because chunk_size counts the duration in seconds.
            return 0

    def split_text(self, text: str, returnTimeStamps = False) -> List[str]:
        """Split text into multiple components."""
        text = StringIO(text)
        parsedWebVTT = webvtt.read_buffer(text)
        splits = [f"{elem.start} --> {elem.end}\n{elem.text}" for elem in parsedWebVTT]
        merges = self._merge_splits(splits, separator = " ")
        if not returnTimeStamps:
            # Keep only the text
            merges = [re.sub(self.timestampPattern + r".*\n", "", elem) for elem in merges]
        return merges
    
    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            for chunk in self.split_text(text, returnTimeStamps=True):
                allTimestamps = re.findall(self.timestampPattern, chunk)
                startTimestamp = allTimestamps[0][0]
                endTimestamp = allTimestamps[-1][1]
                metadata = {
                    **copy(_metadatas[i]), 
                    "startTimestamp": startTimestamp, 
                    "endTimestamp": endTimestamp
                }
                chunk = re.sub(self.timestampPattern + r".*\n", "", chunk)
                new_doc = Document(
                    page_content=chunk, metadata=metadata
                )
                documents.append(new_doc)
        return documents
    # TODO: Implementar a criação dos documentos com os metadados (metadados passados como argumento + timestamps)