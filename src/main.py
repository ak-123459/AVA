import argparse
import asyncio
import json
import logging
import os
from src.asr.asr_factory import ASRFactory
from src.vad.vad_factory import VADFactory
from src.tts.tts_factory import TTSFactory
from src.llm.llm_factory import LLMFactory

from .server import Server
from dotenv import load_dotenv
import logging



# Create a logger instance
logger = logging.getLogger(__name__)








load_dotenv()


# huggingface token
HUGGING_FACE_TOKEN=os.getenv("HUGGINGFACE_TOKEN")

# nvidia api key
NVC_API_KEY = os.getenv("NVIDIA_STT_API_KEY")


# murf api key
MURF_API_KEY = os.getenv("MURF_TTS_API_KEY")

# llm host api
LLM_HOST_ENDPOINT = os.getenv("LLM_HOST_ENDPOINT")




def parse_args():
    parser = argparse.ArgumentParser(
        description="VoiceStreamAI Server: Real-time audio transcription "
        "using self-hosted Whisper and WebSocket."
    )
    parser.add_argument(
        "--vad-type",
        type=str,
        default="pyannote",
        help="Type of VAD pipeline to use (e.g., 'pyannote')",
    )
    parser.add_argument(
        "--vad-args",
        type=str,
        default=f'{{"auth_token": "{HUGGING_FACE_TOKEN}"}}' ,
        help="JSON string of additional arguments for VAD pipeline",
    )
    parser.add_argument(
        "--asr-type",
        type=str,
        default="nvidia_stt_api",
        help="Type of ASR pipeline to use (e.g., 'whisper')",
    )


    parser.add_argument(
        "--tts-type",
        type=str,
        default="murf",
        help="Type of TTS pipeline to use (e.g., 'murf_api')",
    )




    parser.add_argument(
        "--llm-type",
        type=str,
        default="custom_host_llm",
        help="Type of LLM pipeline to use (e.g., 'murf_api')",
    )



    parser.add_argument(
        "--llm-args",
        type=str,
        default= '{}',
        help="Type of TTS pipeline to use (e.g., 'custom_host_llm')",
    )




    parser.add_argument(
        "--tts-args",
        type=str,
        default= '{}',
        help="Type of TTS pipeline to use (e.g., 'murf_api')",
    )



    parser.add_argument(
        "--asr-args",
        type=str,
        default='{}',

        help="JSON string of additional arguments for ASR pipeline",
    )


    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for the WebSocket server",
    )
    parser.add_argument(
        "--port", type=int, default=8765, help="Port for the WebSocket server"
    )
    parser.add_argument(
        "--certfile",
        type=str,
        default=None,
        help="The path to the SSL certificate (cert file) if using secure "
        "websockets",
    )
    parser.add_argument(
        "--keyfile",
        type=str,
        default=None,
        help="The path to the SSL key file if using secure websockets",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="error",
        choices=["debug", "info", "warning", "error"],
        help="Logging level: debug, info, warning, error. default: error",
    )
    return parser.parse_args()




def main():


    args = parse_args()

# Print the default (or provided) value
    print("VAD Args (string):", args.vad_args)
    logging.basicConfig()
    logging.getLogger().setLevel(args.log_level.upper())

    try:
        vad_args = json.loads(args.vad_args)
        asr_args = json.loads(args.asr_args)
        tts_args = json.loads(args.tts_args)
        llm_args = json.loads(args.llm_args)



         # Inject asr_args values
        asr_args.setdefault("model_size", "large-v3")
        asr_args.setdefault("language_code", "en")
        asr_args.setdefault("server", "grpc.nvcf.nvidia.com:443")
        asr_args.setdefault("use_ssl", True)
        asr_args.setdefault("ssl_cert", None)
        asr_args.setdefault("test_file", "")
        asr_args["api_key"] = NVC_API_KEY
        asr_args["metadata"] = [
        ["function-id", "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"],
        ["authorization", f"Bearer {NVC_API_KEY}"]]




        # Inject tts_args values
        tts_args.setdefault("format", "WAV")
        tts_args.setdefault("sample_rate", "44100")
        tts_args.setdefault("voice_id", "hi-IN-shweta")
        tts_args["MURF_TTS_API_KEY"] = MURF_API_KEY



        # Inject llm_args values
        llm_args['host'] = LLM_HOST_ENDPOINT

        llm_args['payloads'] = '{"query":"Hello","last_3_turn":[{"role":"user","content":""},{"role":"assistant","content":""}]}'

        llm_args['endpoint'] = "/chat"


    except json.JSONDecodeError as e:
        print(f"Error parsing JSON arguments: {e}")
        return



    vad_pipeline = VADFactory.create_vad_pipeline(args.vad_type, **vad_args)
    logger.info("VAD object created successfully..")

    asr_pipeline = ASRFactory.create_asr_pipeline(args.asr_type, **asr_args)
    logger.info("ASR(STT) object created successfully..")

    tts_pipeline = TTSFactory.create_tts_pipeline(args.tts_type, **tts_args)
    logger.info("TTS object created successfully..")

    llm_pipeline = LLMFactory.create_llm_pipeline(args.llm_type, **llm_args)
    logger.info("LLM inference class object created successfully..")




    server = Server(
        vad_pipeline,
        asr_pipeline,
        tts_pipeline,
        llm_pipeline,
        host=args.host,
        port=args.port,
        sampling_rate=16000,
        samples_width=2,
        certfile=args.certfile,
        keyfile=args.keyfile,
    )

    asyncio.get_event_loop().run_until_complete(server.start())
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
