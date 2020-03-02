import numpy as np
from functools import reduce

class Tranche(object):

    def __init__(self, tranche_id, face_value, notional_percent,
                 coupon_rate, subordination_level,
                 price=None
                 ):
        self._tranche_id = tranche_id
        self._face_value = face_value
        self._notional_percent = notional_percent
        self._coupon_rate = coupon_rate
        self._subordination_level = subordination_level
        if price is None:
            self._price = face_value
        else:
            self._price = price

    @property
    def trancheID(self):
        return self._tranche_id

    @trancheID.setter
    def trancheID(self, itrancheID):
        self._tranche_id = itrancheID

    @property
    def face_value(self):
        return self._face_value

    @face_value.setter
    def face_value(self, iface_value):
        self._face_value = iface_value

    @property
    def notional_percent(self):
        return self._notional_percent

    @notional_percent.setter
    def notional_percent(self, inotional_percent):
        self._notional_percent = inotional_percent

    @property
    def coupon_rate(self):
        return self._coupon_rate

    @coupon_rate.setter
    def coupon_rate(self, icoupon_rate):
        self._coupon_rate = icoupon_rate

    @property
    def subordination_level(self):
        return self._subordination_level

    @subordination_level.setter
    def subordination_level(self, isubordination_level):
        self._subordination_level = isubordination_level

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, iprice):
        self._price = iprice

    def IRR(self, payments):
        return np.irr([-1 * self._price] + payments) * 12

    def duration(self, payments):
        irr = self.IRR(payments)
        payment_periods = [i + 1 for i in range(len(payments))]
        duration = np.sum(map(lambda payment_period, payment:
                              payment_period * payment / ((1 + irr)**payment_period),
                              payment_periods, payment
                              )) / self._price
        return duration




