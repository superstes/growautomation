# processing of special condition matches

from core.utils.debug import device_log

from datetime import datetime


class Go:
    def __init__(self, condition, device):
        self.condition = condition
        self.name = device

    def get(self) -> bool:
        if self.condition.check_instance.name == 'time':
            return self._time(raw_value=self.condition.value.copy())

        elif self.condition.check_instance.name == 'date':
            return self._date(raw_value=self.condition.value.copy())

        elif self.condition.check_instance.name.startswith('day_'):
            return self._day()

        device_log(f"Condition match \"{self.condition.name}\" has an unsupported special match set: \"{self.condition.check_instance.name}\"", add=self.name, level=4)
        raise ValueError(f"Unsupported special match type for condition \"{self.condition.name}\"")

    def _time(self, raw_value: str, date: datetime = None) -> bool:
        """
        Will compare the configured time against the current time.
        Is also used for datetime comparison.
        Supported formats:
        - 20
        - 2000
        - 20:00:00
        - 200000

        :param date: A date in format datetime can be passed
        :return: bool
        """

        if date is None:
            date = datetime.now().strftime('%Y%m%d')

        else:
            date = date.strftime('%Y%m%d')

        time = datetime.strptime(f'{date}{self._parse_time(raw_value=raw_value)}', '%Y%m%d%H%M%S')

        return self._datetime_compare(value=time, equal_format='%Y%m%d%H%M')

    def _date(self, raw_value: str, out_date=False) -> (bool, datetime):
        """
        Will compare the configured time against the current time.
        Is also used for datetime comparison.
        Supported formats:
        - 05-12-2020
        - 02032021
        - 01.05.2020

        :return: bool
        """

        date = raw_value.replace('-', '').replace('.', '')

        try:
            value = datetime.strptime(date, '%d%m%Y')

            if out_date:
                return value

            else:
                return self._datetime_compare(value=value, equal_format='%Y%m%d')

        except (ValueError, TypeError):
            self._parse_error()

        pass

    def _datetime(self):
        """
        Will compare the configured date-time against the current time.
        Is also used for datetime comparison.

        Supported formats:
        - 05-12-2020 20:00
        - 05122020 200000
        - 01.05.2020 20
        :return: bool
        """

        separator = ' '
        raw_value = self.condition.value.copy().strip()

        raw_date, raw_time = raw_value.split(separator)
        date = self._date(raw_value=raw_date, out_date=True)

        return self._time(raw_value=raw_time, date=date)

    def _day(self) -> bool:
        """
        Can compare either the day of the week or the day of the month.

        :return: bool
        """

        check_type = self.condition.check_instance.name
        raw_value = self.condition.value

        if check_type == 'day_week':
            day = datetime.today().weekday() + 1

            try:
                value = int(raw_value.strip())

            except ValueError:
                if raw_value in ['MO', 'MON', 'mo', 'MON']:
                    value = 1

                elif raw_value in ['DI', 'TUE', 'di', 'tue']:
                    value = 2

                elif raw_value in ['MI', 'WED', 'mi', 'wed', 'WE', 'we']:
                    value = 3

                elif raw_value in ['DO', 'THU', 'thu', 'do', 'th', 'TH']:
                    value = 4

                elif raw_value in ['FR', 'FRI', 'fr', 'fri']:
                    value = 5

                elif raw_value in ['SA', 'SAT', 'sa', 'sat']:
                    value = 6

                elif raw_value in ['SO', 'SUN', 'SU', 'so', 'SUN', 'su']:
                    value = 7

                else:
                    self._parse_error()

            return self._compare_day(value=value, compare=day)

        elif check_type == 'day_month':
            day = datetime.today().day

            try:
                value = int(raw_value.strip())
                return self._compare_day(value=value, compare=day)

            except ValueError:
                self._parse_error()

        else:
            self._parse_error()

    def _compare_day(self, value: int, compare: int) -> bool:
        """
        Simple comparison of current day against the match-day.

        :param value: Day to match
        :param compare: Current day
        :return: bool
        """
        operator = self.condition.operator
        result = False

        if operator == '=':
            if value == compare:
                result = True

        elif operator == '!=':
            if value != compare:
                result = True

        elif operator == '>':
            if value > compare:
                result = True

        elif operator == '<':
            if value < compare:
                result = True

        else:
            device_log(f"Condition match \"{self.condition.name}\" has an unsupported operator \"{operator}\"", add=self.name, level=4)
            raise ValueError(f"Unsupported operator for condition \"{self.condition.name}\"")

        return result

    def _datetime_compare(self, value: datetime, equal_format: str):
        """
        Will compare a given datetime to the current one.

        :param value: Datetime to match
        :param equal_format: Datetime format used for equality check
        :return: bool
        """
        now = datetime.now()
        operator = self.condition.operator
        result = False

        def _equal(_now, _data) -> bool:
            # will use custom time format since some make no sense for this comparison
            if now.strftime(equal_format) == value.strftime(equal_format):
                return True

            return False

        if operator == '=':
            result = _equal(now, value)

        elif operator == '!=':
            result = not _equal(now, value)

        elif operator == '>':
            if value > now:
                result = True

        elif operator == '<':
            if value < now:
                result = True

        else:
            device_log(f"Condition match \"{self.condition.name}\" has an unsupported operator \"{operator}\"", add=self.name, level=4)
            raise ValueError(f"Unsupported operator for condition \"{self.condition.name}\"")

        device_log(f"Condition match \"{self.condition.name}\" result for comparison \"{value} {operator} {now}\" = {result}", add=self.name, level=7)
        return result

    def _parse_time(self, raw_value: str) -> int:
        # find out what format is used
        raw_value.replace(':', '').strip()

        try:
            raw_value = int(raw_value)

            if len(str(raw_value)) == 1:
                value = int(f'0{raw_value}0000')

            elif len(str(raw_value)) == 2:
                value = int(f'{raw_value}0000')

            elif len(str(raw_value)) == 4:
                value = int(f'{raw_value}00')

            elif len(str(raw_value)) == 6:
                value = raw_value

            else:
                raise ValueError

            return value

        except (TypeError, ValueError):
            self._parse_error()

    def _parse_error(self):
        device_log(f'Unable to parse {self.condition.check_instance.name} value provided for condition match \"{self.condition.name}\". '
                   f'Please check the documentation for supported formats.', add=self.name, level=4)
        raise ValueError(f'Unsupported value for condition match \"{self.condition.name}\"')
