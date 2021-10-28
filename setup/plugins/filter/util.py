class FilterModule(object):

    def filters(self):
        return {
            "all_true": self.all_true,
        }

    @staticmethod
    def all_true(data: list) -> bool:
        return all(data)
