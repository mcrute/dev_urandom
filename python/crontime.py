# vim: set filencoding=utf8
"""
Cron Time - Translates Cron-English and the Converse

@author: Mike Crute (mcrute@ag.com)
@organization: American Greetings Interactive
@date: September 08, 2009
"""


class ParseError(Exception): pass


class EnglishParser(object):

    PERIODICALS = {
        'day': (0, 0, None, None, None),
        'hour': (0, None, None, None, None),
        }

    STEMMING = {
        'daily': 'day',
        'hourly': 'hour',
        }

    def to_cron(self, timestr):
        candidate = timestr.split(' ')

        if 'every' in candidate:
            candidate = self._handle_every(candidate)

        if len(candidate) == 1:
            entry = self._handle_simple(candidate[0])

        return self._make_cron(entry)

    def _handle_simple(self, expression):
        if expression in self.PERIODICALS:
            return self.PERIODICALS[expression]

        raise ParseError("Can't parse '{0}'.".format(expression))

    def _handle_every(self, expression):
        pass

    def _make_cron(self, entry):
        cron_entry = CronEntry()
        cron_entry.minute = entry[0]
        cron_entry.hour = entry[1]
        cron_entry.day_of_month = entry[2]
        cron_entry.month = entry[3]
        cron_entry.day_of_week = entry[4]
        return cron_entry


class CronEntry(object):

    minute = None
    hour = None
    day_of_month = None
    month = None
    day_of_week = None

    def __init__(self, **kwargs):
        for key, val in kwargs:
            if key in type(self).__dict__:
                self.__dict__[key] = val

    def __str__(self):
        entry = [self._format_entry(self.minute)]
        entry.append(self._format_entry(self.hour))
        entry.append(self._format_entry(self.day_of_month))
        entry.append(self._format_entry(self.month))
        entry.append(self._format_entry(self.day_of_week))
        return ' '.join(entry)

    def _format_entry(self, unit):
        if unit is None:
            return '*'

        if hasattr(unit, '__iter__'):
            return ','.join(unit)

        return str(unit)
