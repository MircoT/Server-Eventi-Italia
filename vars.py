def singleton(cls):
    """Singleton decorator
    """
    instances = {}
    def getinstance(* args):
        """Check if class instance exists
        """
        if cls not in instances:
            instances[cls] = cls(* args)
        return instances[cls]
    return getinstance

convertName = lambda name: name.lower().capitalize()