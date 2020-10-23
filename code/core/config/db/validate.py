# validates data loaded from db
# validates data that should be written to db


class Go:
    def __init__(self, data):
        self.data = data

    def get(self):
        return self.data
