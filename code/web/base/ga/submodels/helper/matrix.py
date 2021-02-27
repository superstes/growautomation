from json import dumps as json_dumps
from json import loads as json_loads


class Matrix:
    MAX_JSON_LEN = 30000

    def __init__(self, x: int = None, y: int = None, matrix: str = None):
        if matrix is None:
            self.x = x
            self.y = y
            self.matrix = self._gen()
        else:
            self.matrix = self._json_input(matrix)

    def set(self, xy_data: dict, set_value: int) -> bool:
        if self._valid_xy_data(xy_data=xy_data):
            free, used_list = self.check(xy_data=xy_data)
            if free:
                if self._set_fields(xy_data=xy_data, set_value=set_value):
                    return True

                else:
                    return False

            else:
                # print("unable to set field '%s' since the following fields are already present: '%s'" % (set_value, used_list))
                return False

        else:
            # print("invalid xy_data")
            return False

    def check(self, xy_data: dict) -> tuple:
        if self._valid_xy_data(xy_data=xy_data):
            free = True
            used_list = []

            for y in range(xy_data['y0'], xy_data['y1'] + 1):
                y_data = self.matrix[y - 1]

                for x in range(xy_data['x0'], xy_data['x1'] + 1):
                    x_data = y_data[x - 1]

                    if x_data != 0:
                        free = False
                        used_list.append("%s/%s=%s" % (y, x, x_data))

            return free, used_list

        return False, []

    def get(self):
        return self._json_output(self.matrix)

    @staticmethod
    def _json_input(matrix: str) -> list:
        return json_loads(matrix)

    @staticmethod
    def _json_output(matrix: list) -> str:
        return json_dumps(matrix)

    def _set_fields(self, xy_data: dict, set_value: int):
        _matrix = self.matrix.copy()
        for y in range(len(_matrix)):
            if y in range(xy_data['y0'] - 1, xy_data['y1']):
                for x in range(xy_data['x0'], xy_data['x1'] + 1):
                    _matrix[y][x - 1] = set_value

        if len(self._json_output(_matrix)) > self.MAX_JSON_LEN:
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
    def _valid_xy_data(xy_data: dict):
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
