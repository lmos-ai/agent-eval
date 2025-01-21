from lib.singleton import SingletonClass
from openai import AzureOpenAI
from openai import OpenAI
from global_variable import LOCAL_LLM, AZURE_LLM, LLM_SOURCES, OPENAI_LLM


class LLMModel(metaclass=SingletonClass):
    def __init__(self, llm_endpoint:str=None, api_key:str=None, model_name:str="o1-mini", 
                 model_source:str=AZURE_LLM, temperature:float=0.3, azure_api_version="2023-06-01-preview") -> None:
        self.model_name = model_name

        self.model = self.get_llm(
            llm_endpoint=llm_endpoint,
            model_source=model_source,
            api_key=api_key, 
            temperature=temperature,
            model_name=model_name,
            azure_api_version=azure_api_version
            )

    def get_llm(self, model_source:str, llm_endpoint:str, model_name:str, api_key:str, azure_api_version:str, temperature:float=0.3, ):
        """
        This function will intialize the OpenAI LLM and return LLM instance.
        Args:
            model_source (String): Define the source of llm like azure, local.
            llm_endpoint (String): Endpoint of llm if you are using local or azure openai
            model_name (String): Version of model like gpt-3.5
            api_key (String): API Key for LLM if required.
            azure_api_version (String): Version of LLM deployed in Azure
            temperature (String): Randomness propert. Range between 0 to 1
        """
        try:
            if model_source not in LLM_SOURCES:
                # check if llm sources are valid or not
                raise ValueError(f"model_source passed does not match: {LLM_SOURCES}")
            self.model_source = model_source
            if model_source == AZURE_LLM:
                # do validations for Azure LLM initalization
                if not model_name:
                    raise ValueError("Pass correct model_name. Eg. gpt-4o")
                elif not api_key:
                    raise ValueError(f"Pass correct Api key. Passed API key is: {api_key}")
                elif not llm_endpoint:
                    raise ValueError(f"Pass correct Azure LLM endpoint. You passed: {llm_endpoint}")
                #return azure opneAI llm
                return AzureOpenAI(
                    api_key=api_key,
                    azure_endpoint=llm_endpoint,
                    api_version=azure_api_version
                )
            elif model_source == OPENAI_LLM:
                if not model_name:
                    raise ValueError("Pass correct model_name. Eg. gpt-4o")
                elif not api_key:
                    raise ValueError(f"Pass correct Api key. Passed API key is: {api_key}")
                return OpenAI(api_key=api_key, base_url=llm_endpoint)

            # elif model_source == LOCAL_LLM:
            #     if not model_name:
            #         raise ValueError("Pass correct model_name. Eg. llama3")
            #     # return local llm
            #     return Ollama(model=model_name, base_url=llm_endpoint or "http://localhost:11434", request_timeout=120)
            
        except Exception as e:
            print(f"Error in intializing the LLM. Error is :{e}")
            raise Exception("LLM not intialized.") from e 
        
    def complete(self, text, format=None, verbose=False):
        """
        This function will pass the text to LLM and will return the 
        response from LLM in text format.
        """
        # check if llm is initalized
        if self.model is None:
            raise ValueError("LLM is not initialized. Please initialize it first.")
        try:
            if self.model_source == AZURE_LLM:
                completion = self.model.chat.completions.create(
                    model=self.model_name, 
                    messages=[
                        {"role": "user", "content": text},
                    ],
                    max_tokens=2000,
                )
                if verbose:
                    print(completion.choices)
                return completion.choices[0].message.content
            elif self.model_source == OPENAI_LLM:
                response = self.model.chat.completions.create(
                    model=self.model_name,
                    messages=[
                            {"role": "user", "content": text},
                        ],
                    # response_format={ "type": "json_object" }
                )
                return response.choices[0].message.content
            
        except Exception as e:
            print("Exception: Error in calling LLM", e)
            return None

        




        