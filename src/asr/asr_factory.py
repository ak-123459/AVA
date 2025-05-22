from .faster_whisper_asr import FasterWhisperASR
from .whisper_asr import WhisperASR
from .nvidia_stt.asr import Nvidia_STT_API


class ASRFactory:
    @staticmethod
    def create_asr_pipeline(asr_type, **kwargs):

        if asr_type == "whisper":

            return WhisperASR(**kwargs)

        if asr_type == "faster_whisper":

            return FasterWhisperASR(**kwargs)

        if asr_type == "nvidia_stt_api":

            return Nvidia_STT_API( **kwargs)

        else:

            raise ValueError(f"Unknown ASR pipeline type: {asr_type}")
