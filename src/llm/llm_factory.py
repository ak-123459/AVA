from .custom_host_llm import CustomHostLLM
import logging




class LLMFactory:
    @staticmethod
    def create_llm_pipeline(llm_type, **kwargs):

        if llm_type == "custom_host_llm":

            return CustomHostLLM(**kwargs)



        else:


            raise ValueError(f"Unknown LLM pipeline type: {llm_type}")
