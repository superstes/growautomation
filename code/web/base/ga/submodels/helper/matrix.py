from json import dumps as json_dumps
from json import loads as json_loads

from ...config.model import DB_MATRIX_MAX_JSON_LEN


class Matrix:
    MAX_JSON_LEN = DB_MATRIX_MAX_JSON_LEN

    def __init__(self, x: int = None, y: int = None, matrix: str = None):
        if matrix is None:
            self.x = x
            self.y = y
            self.matrix = self._gen()

        else:
            self.matrix = self._json_input(matrix)

    def set(self, xy_data: dict, set_value: int) -> bool:
        """ Adds data to the matrix if it is valid """
        if self._valid_xy_data(xy_data=xy_data):
            free, used_list = self.check(xy_data=xy_data)
            if free or set_value == 0:
                return self._set_fields(xy_data=xy_data, set_value=set_value)

            else:
                # log error or whatever ("unable to set field '%s' since the following fields are already present: '%s'" % (set_value, used_list))
                return False

        else:
            # log error or whatever ("invalid xy_data")
            return False

    def check(self, xy_data: dict) -> tuple:
        """ Checks if provided area is empty or in use """
        if self._valid_xy_data(xy_data=xy_data):
            free = True
            used_list = []

            for y in range(xy_data['y0'], xy_data['y1'] + 1):
                y_data = self.matrix[y - 1]

                for x in range(xy_data['x0'], xy_data['x1'] + 1):
                    x_data = y_data[x - 1]

                    if x_data != 0:
                        free = False
                        used_list.append(f"{y}/{x}={x_data}")

            return free, used_list

        # log error or whatever
        return False, []

    def get(self) -> str:
        return self._json_output(self.matrix)

    def free(self, xy_data: dict, used: bool = False, both: bool = False) -> (list, tuple):
        """ Checks dashboard matrix for unused/used/or both positions in the provided area """
        free_list = []
        used_list = []

        for y in range(xy_data['y0'], xy_data['y1'] + 1):
            _row = self.matrix[y - 1]
            for x in range(xy_data['x0'], xy_data['x1'] + 1):
                _col = _row[x - 1]

                if _col == 0:
                    free_list.append({'x': x, 'y': y})

                elif _col != 0:
                    used_list.append({'x': x, 'y': y, 'value': _col})

        if both:
            return free_list, used_list

        elif used:
            return used_list

        else:
            return free_list

    @staticmethod
    def _json_input(matrix: str) -> list:
        return json_loads(matrix)

    @staticmethod
    def _json_output(matrix: list) -> str:
        return json_dumps(matrix)

    def _set_fields(self, xy_data: dict, set_value: int) -> bool:
        _matrix = self.matrix.copy()
        for y in range(len(_matrix)):
            if y in range(xy_data['y0'] - 1, xy_data['y1']):
                for x in range(xy_data['x0'], xy_data['x1'] + 1):
                    _matrix[y][x - 1] = set_value

        if len(self._json_output(_matrix)) > DB_MATRIX_MAX_JSON_LEN:
            # log error or whatever
            return False

        else:
            self.matrix = _matrix
            return True

    def _gen(self):
        matrix = []
        for y in range(self.y):
            row = []

            for x in range(self.x):
                row.append(0)

            matrix.append(row.copy())

        return matrix

    @staticmethod
    def _valid_xy_data(xy_data: dict) -> bool:
        valid = True
        must_have = ['y0', 'y1', 'x0', 'x1']

        for field in must_have:
            if field not in xy_data:
                valid = False

        try:
            if int(xy_data['y0']) > int(xy_data['y1']):
                valid = False

            if int(xy_data['x0']) > int(xy_data['x1']):
                valid = False

        except ValueError:
            valid = False

        return valid
