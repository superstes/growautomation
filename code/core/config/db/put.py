# writes data to db


class Go:
    def __init__(self, link):
        self.link = link

    def get(self):
        return self.link