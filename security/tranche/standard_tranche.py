import logging
from .tanche_base import Tranche


class StandardTranche(Tranche):
    def __init__(self, tranche_id, face_value, notional_percent,
                 coupon_rate, subordination_level, OC_tranche = False,
                 price=None):
        super(StandardTranche, self).__init__(tranche_id, face_value, notional_percent,
                                              coupon_rate, subordination_level,
                                              price)
        self._current_time_period = 0
        self._current_principle_paid = 0
        self._current_notional_balance = self.face_value
        self._current_interest_paid = 0
        self._current_interest_due = 0
        self._current_interest_shortfall = 0
        self._OC_tranche = OC_tranche

    @property
    def currentPeriod(self):
        return self._current_time_period

    @property
    def interestDue(self):
        return self._current_interest_due

    @property
    def interestPaid(self):
        return self._current_interest_paid

    @property
    def pinciplaPaid(self):
        return self._current_principle_paid

    @property
    def interestShortFall(self):
        return self._current_interest_shortfall

    @property
    def current_notional_balance(self):
        return self._current_notional_balance

    @property
    def OC(self):
        return self._OC_tranche

    def timeIncrease(self):
        self._current_time_period += 1
        self._current_interest_due = self.coupon_rate / 12 * self._current_notional_balance + self._current_interest_shortfall
        # balance and intest update in receive_payment
        self._current_interest_paid = 0
        self._current_principle_paid = 0
        self._current_interest_shortfall = 0

    def receivePrincipalPayment(self, available_cash, period=1):
        if self._current_notional_balance == 0:
            logging.info('Tranche {t} has 0 balance and no need to pay'.format(t=self._tranche_id))
        else:
            self._current_principle_paid = min(self._current_notional_balance,
                                               available_cash
                                               )
            self._current_notional_balance -= self._current_principle_paid
        return available_cash - self._current_principle_paid

    def receiveInterestPayment(self, available_cash, period=1):
        if self._current_interest_due == 0:
            logging('Tranche {t} has 0 interest due and no need to pay interest'.format(t=self._tranche_id))
        else:
            self._current_interest_paid = min(self._current_interest_due, available_cash)
            self._current_interest_shortfall = self._current_interest_due - self._current_interest_paid
        return available_cash - self._current_interest_paid

    def reset(self):
        self._current_time_period = 0
        self._current_principle_paid = 0
        self._current_notional_balance = self.face_value
        self._current_interest_paid = 0
        self._current_interest_due = 0
        self._current_interest_shortfall = 0
