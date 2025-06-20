import asyncio
import json
import os
import time
from dotenv import load_dotenv
import requests
import logging
from .buffering_strategy_interface import BufferingStrategyInterface

# Create logging instance
logger = logging.getLogger(__name__)






async  def send_audio_byte(websocekt):

     with open("C:\\Users\mishr\Downloads\\test_filewav.wav", "rb") as audio_file:

       while chunk := audio_file.read(1024):


           await  websocekt.send(chunk)

       await websocekt.send("EOF")  # signal the end



class SilenceAtEndOfChunk(BufferingStrategyInterface):
    """
    A buffering strategy that processes audio at the end of each chunk with
    silence detection.

    This class is responsible for handling audio chunks, detecting silence at
    the end of each chunk, and initiating the transcription process for the
    chunk.

    Attributes:
        client (Client): The client instance associated with this buffering
                         strategy.
        chunk_length_seconds (float): Length of each audio chunk in seconds.
        chunk_offset_seconds (float): Offset time in seconds to be considered
                                      for processing audio chunks.
    """

    def __init__(self, client, **kwargs):
        """
        Initialize the SilenceAtEndOfChunk buffering strategy.

        Args:
            client (Client): The client instance associated with this buffering
                             strategy.
            **kwargs: Additional keyword arguments, including
                      'chunk_length_seconds' and 'chunk_offset_seconds'.
        """
        self.client = client

        self.chunk_length_seconds = os.environ.get(
            "BUFFERING_CHUNK_LENGTH_SECONDS"
        )
        if not self.chunk_length_seconds:
            self.chunk_length_seconds = kwargs.get("chunk_length_seconds")
        self.chunk_length_seconds = float(self.chunk_length_seconds)

        self.chunk_offset_seconds = os.environ.get(
            "BUFFERING_CHUNK_OFFSET_SECONDS"
        )
        if not self.chunk_offset_seconds:
            self.chunk_offset_seconds = kwargs.get("chunk_offset_seconds")
        self.chunk_offset_seconds = float(self.chunk_offset_seconds)

        self.error_if_not_realtime = os.environ.get("ERROR_IF_NOT_REALTIME")
        if not self.error_if_not_realtime:
            self.error_if_not_realtime = kwargs.get(
                "error_if_not_realtime", False
            )

        self.processing_flag = False





    def process_audio(self, websocket, vad_pipeline, asr_pipeline,tts_pipeline,llm_pipeline):

        """
        Process audio chunks by checking their length and scheduling
        asynchronous processing.

        This method checks if the length of the audio buffer exceeds the chunk
        length and, if so, it schedules asynchronous processing of the audio.

        Args:
            websocket: The WebSocket connection for sending transcriptions.
            vad_pipeline: The voice activity detection pipeline.
            asr_pipeline: The automatic speech recognition pipeline.
        """
        chunk_length_in_bytes = (
            self.chunk_length_seconds
            * self.client.sampling_rate
            * self.client.samples_width
        )
        if len(self.client.buffer) > chunk_length_in_bytes:
            if self.processing_flag:
                exit(
                    "Error in realtime processing: tried processing a new "
                    "chunk while the previous one was still being processed"
                )

            self.client.scratch_buffer += self.client.buffer
            self.client.buffer.clear()
            self.processing_flag = True

            # Schedule the processing in a separate task
            asyncio.create_task(
                self.process_audio_async(websocket, vad_pipeline, asr_pipeline,tts_pipeline,llm_pipeline)
            )

    async def process_audio_async(self, websocket, vad_pipeline, asr_pipeline,tts_pipeline,llm_pipeline):



            """
            Asynchronously process audio for activity detection and transcription.

            This method performs heavy processing, including voice activity
            detection and transcription of the audio data. It sends the
            transcription results through the WebSocket connection.

            Args:
                websocket (Websocket): The WebSocket connection for sending
                                       transcriptions.
                vad_pipeline: The voice activity detection pipeline.
                asr_pipeline: The automatic speech recognition pipeline.
            """
            start = time.time()

            vad_results = await vad_pipeline.detect_activity(self.client)

            end =time.time()

            print("activity_detection_time:----",end-start)

            if len(vad_results) == 0:
                self.client.scratch_buffer.clear()
                self.client.buffer.clear()
                self.processing_flag = False
                return

            last_segment_should_end_before = (
                len(self.client.scratch_buffer)
                / (self.client.sampling_rate * self.client.samples_width)
            ) - self.chunk_offset_seconds

            if vad_results[-1]["end"] < last_segment_should_end_before:

                    await websocket.send(json.dumps({"type": "process"}))

                    try:

                        speech_to_text = asr_pipeline.transcribe(self.client)


                        if not speech_to_text:

                            await websocket.send(json.dumps({"type": "error","value":"speech to text module error"}))

                            logger.error("Error in speech to text module...")
                            return

                        
                        # get llm response 
                        llm_response = llm_pipeline.generate_response({"query":speech_to_text,"last_3_turn":[{"role":"user","content":""},{"role":"assistant","content":""}]})


                        if not llm_response:

                            await websocket.send(json.dumps({"type": "error","value":"LLM is not responding.."}))

                            logger.error("LLM response was empty...")

                            return

                        # tts pipeline
                        
                        text_to_speech = tts_pipeline.speech_synthesis(llm_response)


                        if not text_to_speech:

                            await websocket.send(json.dumps({"type": "error","value":"text to speech not working.."}))
                            logger.error("No audio file returned from TTS.")

                            return


                        # ✅ Send audio url only if everything succeeded
                        await websocket.send(json.dumps({"type":"url","value":text_to_speech}))


                    finally:
                        # ✅ Always clean up — even if there was an error
                        self.client.scratch_buffer.clear()
                        self.client.increment_file_counter()


            self.processing_flag = False
