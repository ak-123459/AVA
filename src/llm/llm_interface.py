class LLMInterface:


    async def generate_response(self, payloads:dict=None):
        """
        Generate the response from self host LLM from the given payloads.

        :param payloads: post request payloads for API call

        :return: The generated respose from hosted LLM.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses."
        )
