from .tts_interface import TTSInterface
import requests
from murf import Murf
import os
import logging
import inspect

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


  
  async def  synthesise_stream_audio(self,text:str=None):

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





  async def speech_synthesis(self,text:str=None,client=None):

    if(client is not None):

        file_name =  client.get_file_name()
    else:

      file_name = self.output_file

    res = self.murf_client.text_to_speech.generate(text= text,  voice_id=self.voice_id, format = self.format, sample_rate =self.sample_rate)
    
    
    url = res.audio_file
    


    r = requests.get(url)


    if(r.status_code==200):  
  
    
      with open( file_name, 'wb') as f:

         f.write(r.content)
        
      print("text to speech completed.")   
    
    else:
    
      print("murf source audio file not found")

   
    os.remove(file_name)

    logger.info("Murf text to speech file  created...")
   
  






           
