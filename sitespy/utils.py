class DataManager:
    """
    Singleton manager for data and config.
    Supporting only Mac OS for prototype purposes.
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            return cls.__instance
        return cls.__instance

    def __init__(self):
        pass
