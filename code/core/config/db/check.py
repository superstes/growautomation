# should check for db connectivity problems before connecting


class Go:
    def __init__(self, connection_data_dict):
        self.connection_data_dict = connection_data_dict

    def get(self):
        try:
            self._test_network()
            self._test_credentials()
        except (mysql.connector.Error, ConnectionError) as error_msg:
            self._error(msg=error_msg)
            return False
        return True

    def _test_read(self):
        pass

    def _test_write(self):
        # may need to add a ignore argument for server/agent installation (since server db will be r/o for agent)
        pass

    def _test_credentials(self):
        # check access to db
        self._test_read()
        self._test_write()

    def _test_network(self):
        # check <L5 connectivity
        pass

    @staticmethod
    def _error(msg):
        # log error or whatever
        raise ConnectionError('SQL connection test failed')
