from .tranche.standard_tranche import StandardTranche


# TO DOs:
# (1) add customize payment priority
# (2) add trigger mode
# (3) add reserve account condition
# (4) make

class StructuredSecurities(object):
    def __init__(self, total_notional, priority=None):
        self._current_period = 0
        self._total_notional = total_notional
        self._tranche_list = []
        self._mode = 'Sequential'
        self._reserve_account = 0
        self._priority = priority
        self._int_payment_flow = {}
        self._prin_payment_flow = {}
        self._oc_payment_flow = {}

    @property
    def reserve_amount(self):
        return self._reserve_account

    @property
    def tranche_list(self):
        return self._tranche_list

    @property
    def mode(self):
        return self._mode

    @property
    def paymentPriority(self):
        return self._priority

    @paymentPriority.setter
    def paymentPriority(self, ipriority):
        self._priority = ipriority

    def addTranche(self, tranche_id, face_value, notional_percent,
                   coupon_rate, subordination_level,
                   price=None):
        new_tranche = StandardTranche(tranche_id, face_value,
                                      notional_percent, coupon_rate,
                                      subordination_level, price)
        self._tranche_list.append(new_tranche)
        self._tranche_list = sorted(self._tranche_list, key=lambda x: x.subordination_level)

    @classmethod
    def constructSecurities(cls, total_face_value,
                            tranche_ids,
                            notional_percentages,
                            coupon_rates,
                            subordination_levels,
                            priority=None):
        structured_securities = StructuredSecurities(total_face_value)
        for tranche_id, notional_percent, coupon_rate, subordination_level in zip(tranche_ids, notional_percentages,
                                                                                  coupon_rates, subordination_levels):
            structured_securities.addTranche(tranche_id, notional_percent, coupon_rate, subordination_level)
        structured_securities.paymentPriority = priority
        return structured_securities

    @mode.setter
    def mode(self, imode):
        if imode not in ('Sequential', 'Pro Rate'):
            logging.error('invalud mode. (Sequential / Pro Rata)')
        self._mode = imode

    def increaseTimePeriod(self):
        self._current_period += 1
        for tranche in self._tranche_list:
            tranche.timeIncrease()

    def makePayments(self, available_cash):

        for tranche in self._tranche_list:
            if tranche.current_notional_balance > 0 and not tranche.OC:
                available_cash = tranche.receiveInterestPayment(available_cash)
                # record interest payment
                self._int_payment_flow[tranche.trancheID][self._current_period] = tranche.interestPaid

        # make principle payment
        if available_cash > 0:
            if self._mode == 'Sequential':
                for tranche in self._tranche_list:
                    if tranche.current_notional_balance > 0 and available_cash > 0:
                        available_cash = tranche.receivePrincipalPayment(available_cash)
                        # record principle payment
                        self._prin_payment_flow[tranche.trancheID][self._current_period] = tranche.pinciplaPaid
            elif self._mode == 'Pro Rata':
                NonOC_percent = 1 - sum(tranche.notional_percent for tranche in self._tranche_list if tranche.OC)
                tmp_cash_available = 0
                for tranche in self._tranche_list:
                    if not tranche.OC and tranche.current_notional_balance > 0:
                        tmp_cash_available += tranche.receivePrincipalPayment(tranche.current_notional_balance
                                                                              * tranche.notional_percent
                                                                              / NonOC_percent)
                        # record principle payment
                        self._prin_payment_flow[tranche.trancheID][self._current_period] = tranche.pinciplaPaid
                available_cash = tmp_cash_available
        # the last one is to residual
        if available_cash > 0:
            # record OC payment
            self._oc_payment_flow['OC'][self._current_period] = available_cash
