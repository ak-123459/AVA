class TTSInterface:

    async def synthesise_stream_audio(self,text:str=None):
        """
        synthesize the given text data.

        :param client: The client object with all the member variables
                       including the buffer

        :return: The audio streaming audio.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )
