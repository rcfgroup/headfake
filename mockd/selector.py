from mockd.base import ParamList
from mockd.util import create_package_class
import datetime as dt

class Selector(ParamList):
    pass

class DateSelector(Selector):
    pass

class TimeSelector(Selector):
    pass

class DateOfBirthSelector(DateSelector):
    def init_params(self):
        self.dist_cls = create_package_class(self.distribution)(loc=self.mean, scale=self.sd)

    def select_value(self, row):
        age_in_years = self.dist_cls.rvs()
        if age_in_years<self.min or age_in_years>self.max:
            return self.next_value(row)

        age_in_days = age_in_years * 365.25
        dob = dt.datetime.now() - dt.timedelta(days=age_in_days)
        return dob
