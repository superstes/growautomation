# connects to db
# gets connection settings passed from GaDataDb instance

import mysql.connector


class Go:
    def __init__(self, connection_data_dict):
        self.connection_data_dict = connection_data_dict

    def get(self):
        return None
