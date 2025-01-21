class FunctionExtractor:
    """
    Extracts actual functions called in a conversation log.
    """
    def extract_functions(self, log):
        try:
            return log.get("actual_function_calls", [])
        except Exception as e:
            raise ValueError(f"Error extracting functions: {str(e)}")



class SingletonClass(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonClass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
  
