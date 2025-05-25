import os
from pathlib import Path
import grpc
import riva.client
from src.audio_utils import save_audio_to_file
from dotenv import load_dotenv
from src.asr.asr_interface import ASRInterface




# Connection and ASR Configuration for nvidia speech to text api

class Args:


    max_alternatives = 1
    profanity_filter = False
    automatic_punctuation = False
    no_verbatim_transcripts = False
    word_time_offsets = False
    speaker_diarization = False
    diarization_max_speakers = 1
    boosted_lm_words = []
    boosted_lm_score = 4.0
    start_history = 1
    start_threshold = -1.0
    stop_history = 1
    stop_history_eou = -1
    stop_threshold = 0.0
    stop_threshold_eou = -1.0
    custom_configuration = ""

args = Args()



# Nvidia STT API class
class Nvidia_STT_API(ASRInterface):

    def __init__(self, **kwargs):

     self.language_code = kwargs.get("language_code", "en")

     self.metadata = kwargs.get("metadata")
     self.server = kwargs.get("server")
     self.use_ssl = kwargs.get("use_ssl")
     self.ssl_cert =  kwargs.get("ssl_cert")
     self.test_file =  kwargs.get("test_file")



    async def transcribe(self, client=None)->str:

        if client is None:

           input_file = self.test_file

        else:

           input_file = await save_audio_to_file(client.scratch_buffer, client.get_file_name())


        input_file = Path(input_file)


        auth = riva.client.Auth(self.ssl_cert, self.use_ssl, self.server, self.metadata)

        asr_service = riva.client.ASRService(auth)

        if not os.path.isfile(input_file):
            print(f"Invalid input file path: {input_file}")
            return

        config = riva.client.RecognitionConfig(
            language_code=self.language_code,
            max_alternatives=args.max_alternatives,
            profanity_filter=args.profanity_filter,
            enable_automatic_punctuation=args.automatic_punctuation,
            verbatim_transcripts=not args.no_verbatim_transcripts,
            enable_word_time_offsets=args.word_time_offsets or args.speaker_diarization,
        )

        riva.client.add_word_boosting_to_config(config, args.boosted_lm_words, args.boosted_lm_score)
        riva.client.add_speaker_diarization_to_config(config, args.speaker_diarization, args.diarization_max_speakers)
        riva.client.add_endpoint_parameters_to_config(
            config,
            args.start_history,
            args.start_threshold,
            args.stop_history,
            args.stop_history_eou,
            args.stop_threshold,
            args.stop_threshold_eou
        )
        riva.client.add_custom_configuration_to_config(config, args.custom_configuration)

        with input_file.open('rb') as fh:
            data = fh.read()

        try:

            response = asr_service.offline_recognize(data, config)

            response_text = response.results[0].alternatives[0].transcript.strip()

            return response_text


        except grpc.RpcError as e:

            print("error in nvidia stt api",e)


        os.remove(input_file)

