import logging
import numpy as np

#TO DO
##(1) Implement recovery

class Loan(object):

    def __init__(self, loan_id, term, rate,
                 original_amount,
                 current_balance,
                 current_seasoning,
                 current_status,
                 CDR,
                 CPR,
                 credit_attributes,
                 dq_to_default_months=3
                 ):
        self._loan_id = loan_id
        self._term = term
        self._rate = rate
        self._original_amount = original_amount
        self._current_balance = current_balance
        self._current_seasoning = current_seasoning
        self._current_status = current_status
        self._CDR = CDR
        self._CPR = CPR
        self._credit_attributes = credit_attributes
        self._defaulted = False
        self._prepaid = False
        self._prepaid_month = None
        self._default_month = None
        self._loan_active = True
        self._dq_to_default_months = dq_to_default_months
        self._payment_flow = {}
        self._balance = {0: current_balance}
        self._prin_payment = {}
        self._int_payment = {}
        self._charge_off_prin = {}
        self._charge_off_int = {}
        self._curtailment_flow = {}

    @property
    def loan_id(self):
        return self._loan_id

    @loan_id.setter
    def loan_id(self, iloan_id):
        self._loan_id = iloan_id

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, iterm):
        self._term = iterm

    # @property
    # def rate(self):
    #     return self._rate
    #
    # @rate.setter
    # def rate(self, irate):
    #     self._rate = irate

    @property
    def original_amount(self):
        return self._original_amount

    @original_amount.setter
    def original_amount(self, ioriginal_amount):
        self._original_amount = ioriginal_amount

    @property
    def current_balance(self):
        return self._current_balance

    @current_balance.setter
    def current_balance(self, icurrent_balance):
        self._current_balance = icurrent_balance

    @property
    def current_seasoning(self):
        return self._current_seasoning

    @current_seasoning.setter
    def current_seasoning(self, icurrent_seasoning):
        self._current_seasoning = icurrent_seasoning

    @property
    def current_status(self):
        return self._current_status

    @current_status.setter
    def current_status(self, icurrent_status):
        self._current_status = icurrent_status

    @property
    def credit_attibutes(self):
        return self._credit_attributes

    @credit_attibutes.setter
    def credit_attibutes(self, icredit_attributes):
        self._credit_attributes = icredit_attributes

    @property
    def defaulted(self):
        return self._defaulted

    @defaulted.setter
    def defaulted(self, idefault):
        self._defaulted = idefault

    @property
    def prepaid(self):
        return self._prepaid

    @prepaid.setter
    def prepaid(self, iprepaid):
        self._prepaid = iprepaid

    @property
    def CDR_vector(self):
        return self._CDR

    @CDR_vector.setter
    def CDR_vector(self, iCDR_vector):
        self._CDR = iCDR_vector

    @property
    def loan_active(self):
        return self._loan_active

    def rate(self, period):
        # abstract method and need to be overriden
        raise NotImplementedError()

    @classmethod
    def calcScheduledPayment(cls, int_rate, original_amount, term):
        payment = (int_rate / 12) * original_amount / (1 - (1 + int_rate / 12) ** (-term))
        return payment

    @classmethod
    def calcScheduledBalance(cls, int_rate, original_amount, term, seasoning):
        if seasoning > term:
            logging.info('seasoning {s} months is greater than term {t} months'.format(s=seasoning, t=term))
        else:
            balance = original_amount * (1 + int_rate / 12) ** seasoning - cls.calcScheduledPayment(int_rate,
                                                                                                    original_amount,
                                                                                                    term) * (
                              ((1 + int_rate / 12) ** seasoning - 1) / (int_rate / 12)
            )
            return balance

    def loan_default(self, period):
        self._defaulted = True
        self._default_month = period
        self._loan_active = False

    def loan_prepaid(self, period):
        self._prepaid = True
        self._prepaid_month = period
        self._loan_active = False

    def make_monthly_payment(self, period):
        if self._defaulted:
            self._payment_flow[period] = 0
            # reset previous payment to 0 since they are dq
            if period == self._default_month:
                for mon in range(1, 1 + self._dq_to_default_months):
                    if period - mon > 0:
                        self._payment_flow[period - mon] = 0
            return 0
        elif self._prepaid:
            # if prepaid, the current month payment is previous month balance plus accrued interest
            if period == self._prepaid_month:
                self._payment_flow[period] = self._balance[period - 1] * (1 + self._rate / 12)
                return self._payment_flow[period]
            else:
                self._payment_flow[period] = 0
                return 0
        else:
            payment = self.calcScheduledPayment(self._rate, self._original_amount, self._term)
            # if balance less than scheduled payment, then payment equals to balance and loan prepaid
            if self._balance[period - 1] * (1 + self._rate / 12) <= payment:
                payment = self._balance[period - 1] * (1 + self._rate / 12)
                self.loan_prepaid(period)
            self._payment_flow[period] = payment
            return payment

    def make_interest_payment(self, period):
        if self._defaulted:
            self._int_payment[period] = 0
            # if loan defaults this month, then modify previous dq_to_default_months' int_payment
            if period == self._default_month:
                for mon in range(1, 1 + self._dq_to_default_months):
                    if period - mon > 0:
                        self._int_payment[period - mon] = 0
            return 0
        else:
            int_payment = self._balance[period - 1] * (self._rate / 12)
            self._int_payment[period] = int_payment
            return int_payment

    def make_prin_payment(self, period):
        principle_payment = self._payment_flow[period] - self._int_payment[period]
        self._prin_payment[period] = principle_payment
        if self._prepaid:
            self._curtailment_flow[period] = principle_payment - (
                    self.calcScheduledPayment(self._rate, self._original_amount, self._term)
                    - self._int_payment[period]
            )
        else:
            self._curtailment_flow[period] = 0
        return principle_payment

    def calc_balance(self, period):
        if self._defaulted:
            if period == self._default_month:
                # if loan defaults, modify previous dq months' balance
                if period <= 3:
                    # charge-off interest equals all accrued interest
                    self._charge_off_int[period] = self._balance[0] * (1 + self._rate/12)**period - self._balance[0] / (1 + self._rate/12)**(self._dq_to_default_months - period + 1)
                    # charge-off principle equals to the principle lost
                    self._charge_off_prin[period] = self._balance[0] / (1 + self._rate/12)**(self._dq_to_default_months - period + 1)
                    for mon in range(1, period):
                        self._balance[mon] = self._balance[0] * (1 + self._rate/12)**mon
                else:
                    self._charge_off_int[period] = self._balance[period - self._dq_to_default_months - 1] * (1 + self._rate/12)**(self._dq_to_default_months + 1) - self._balance[period - self._dq_to_default_months - 1]
                    self._charge_off_prin[period] = self._balance[period - self._dq_to_default_months - 1]
                    for mon in range(1, 1 + self._dq_to_default_months):
                        if period - mon > 0:
                            self._balance[period - mon] = self._balance[period - self._dq_to_default_months - 1] * (1 + self._rate/12)**(self._dq_to_default_months + 1 - mon)
            self._balance[period] = 0
            return 0
        elif self._prepaid:
            self._balance[period] = 0
            self._charge_off_int[period] = 0
            self._charge_off_int[period] = 0
            return self._balance[period]
        else:
            self._charge_off_int[period] = 0
            self._charge_off_int[period] = 0
            balance = self._balance[period - 1] - self._prin_payment[period]
            self._balance[period] = balance
            return self._balance[period]

    def checkStatus(self, rand_prob, period):
        # if loan is still active, then check status
        if self._loan_active == True:
            CDR = self._CDR[period]
            CPR = self._CPR[period]
            sum_p = CDR + CPR
            if sum_p > 1:
                CDR = CDR/sum_p
                CPR = CPR/sum_p
            if rand_prob <= CDR:
                self.loan_default(period)
            # if loan reach to prepay condition or reach to the term then it prepaid
            elif (rand_prob >= (1 - CPR)) or (period + self._current_seasoning == self._term):
                self.loan_prepaid(period)

    def getBalance(self, period):
        return self._balance[period]

    def getPayment(self, period):
        return self._payment_flow[period]

    def getIntPayment(self, period):
        return self._int_payment[period]

    def getPrinciplePayment(self, period):
        return self._prin_payment[period]

    def getCurtailmentPayment(self, period):
        return self._curtailment_flow[period]

    def getChargeOff_prin(self, period):
        return self._charge_off_prin[period]

    def getChargeOff_int(self, period):
        return self._charge_off_int[period]

    # function resets loan status and it is for simulation
    def reset(self):
        self._defaulted = False
        self._prepaid = False
        self._prepaid_month = None
        self._default_month = None
        self._loan_active = True
        self._payment_flow = {}
        self._balance = {0: self._current_balance}
        self._prin_payment = {}
        self._int_payment = {}
        self._charge_off_prin = {}
        self._charge_off_int = {}
        self._curtailment_flow = {}
