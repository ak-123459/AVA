from .llm_interface import LLMInterface
import requests
import json




class CustomHostLLM(LLMInterface):

        
    def __init__(self,**kwargs):
     
     self.host =  kwargs.get("host")
     self.authorization = kwargs.get("authorization","")
     self.content_type = kwargs.get("Content-Type","application/json") 
     self.api_key =  kwargs.get("api_key")
     self.endpoint = kwargs.get("endpoint","/chat")
     self.payloads = kwargs.get("payloads")
     
    
    async def  generate_response(self,payloads:dict=None):

        if(payloads is None):
          
               payloads = self.payloads


        headers = {"Content-Type": self.content_type }


        try:

            response = requests.post(url = self.host+ self.endpoint, headers=headers , data= json.dumps(payloads))

            print("---LLM-RESPONSE - STATUS ---:",response.status_code)


            if(response.status_code==200):

                    return response.json()['response']                      
                    
                          

        except requests.exceptions.RequestException as e:

        # This will catch all types of request-related exceptions

            st.error(f"an error occurred {e}")

        
  

