from .tts_interface import TTSInterface
import requests
from murf import Murf
import os
import logging
import inspect
from urllib.parse import urlparse
# Create a logger instance
logger = logging.getLogger(__name__)




class Murf_tts_api(TTSInterface):


  def __init__(self,**kwargs):

      self.api_key = kwargs.get("MURF_TTS_API_KEY")

      self.murf_client = Murf(api_key = self.api_key)

      self.voice_id = kwargs.get("voice_id","hi-IN-kabir")

      self.format = kwargs.get("format","WAV")

      self.text = kwargs.get("text")
      self.sample_rate = kwargs.get("sample_rate",44100)
      self.output_file = kwargs.get("output_file","tts_test_file.wav")



  async def  synthesise_stream_audio(self,text:str=None)->str:


     if(text is None):
        text = self.text

     res = self.murf_client.text_to_speech.stream(

     text= text,

     voice_id= self.voice_id,    format = self.format, sample_rate =self.sample_rate )


     print("[tts] received streaming object..")

     logger.info("Murf text to speech streaming obeject created...")

     is_generator =  inspect.isgenerator(res)

     if(is_generator):
        return res





  async def speech_synthesis(self,text:str=None)->str:

    global res

    try:

     res =  self.murf_client.text_to_speech.generate(text= text,  voice_id=self.voice_id, format = self.format, sample_rate =self.sample_rate)

    except Exception as e:

         logger.error(f"murf client error {e}")

    # Receiving the audio url

    url = res.audio_file

    try:

        result = urlparse(url)
        # A valid URL should have at least scheme and netloc
        is_valid_url =  all([result.scheme, result.netloc])

        if is_valid_url:

            logger.info("Murf text to speech file  created...")

            return url

    except ValueError:

        logger.error("Murf text to speech error...")

        print("tts error...")












