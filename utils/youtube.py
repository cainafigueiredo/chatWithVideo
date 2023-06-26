import re
from typing import Text, List, Tuple, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter

def extractVideoIDFromURL(url: Text) -> Text:
    videoID = re.findall(r".*v=(.{11}).*", url)[0]
    return videoID

def extractTranscriptsFromVideoID(
    videoID: Text, 
    preprocessFunction = None, 
    languageCodes: List[Text] = ["en"]
) -> Tuple[Dict, Text]:

    availableTranscripts = YouTubeTranscriptApi.list_transcripts(videoID)
    vttFormatter = WebVTTFormatter()
    transcripts = None

    try:
        # Manual transcripts
        transcripts = availableTranscripts.find_manually_created_transcript(language_codes = languageCodes).fetch()
        if preprocessFunction:
            transcripts = [{
                "start": transcript["start"], 
                "duration": transcript["duration"], 
                "text": preprocessFunction(transcript["text"])
            } for transcript in transcripts]
        return vttFormatter.format_transcript(transcripts), "manual"
    except Exception as e: 
        print("Manual transcripts were not found. Trying automatically generated transcripts...")

    try: 
        # Generated transcripts
        transcripts = availableTranscripts.find_generated_transcript(language_codes = languageCodes).fetch() 
        if preprocessFunction:
            transcripts = [{
                "start": transcript["start"], 
                "duration": transcript["duration"], 
                "text": preprocessFunction(transcript["text"])
            } for transcript in transcripts]
        return vttFormatter.format_transcript(transcripts), "generated"
    except Exception as e:
        print("Automatically generated transcripts were not found. Trying to extract transcripts from the video with another tool...")
        # TODO: Implement transcripts extraction using alternative tools
        raise NotImplementedError("It is not possible to extract transcripts from the video with alternative ways because this feature is not implemented yet.")
