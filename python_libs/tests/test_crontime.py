from nose.tools import assert_equals
from crontime import EnglishParser


def assert_str_equals(lhs, rhs):
    assert_equals(str(lhs), rhs)


class TestEnglishParser(object):

    def setup(self):
        self.parser = EnglishParser()

    def test_daily(self):
        daily_cron = '0 0 * * *'
        assert_str_equals(self.parser.to_cron('daily'), daily_cron)
        assert_str_equals(self.parser.to_cron('every day'), daily_cron)

    def test_hourly(self):
        hourly_cron = '0 * * * *'
        assert_str_equals(self.parser.to_cron('hourly'), hourly_cron)
