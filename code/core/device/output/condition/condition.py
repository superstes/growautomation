# processes conditions for output execution


class Go:
    def __init__(self, instance, reverse: bool = False):
        self.instance = instance
        self.reverse = reverse  # if reverse -> the reverse condition must be met

    def get(self) -> bool:
        return True
