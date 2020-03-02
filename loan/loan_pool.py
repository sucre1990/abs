from .loan_base import Loan
import numpy as np


class LoanPool(object):
    def __init__(self, loan_list):
        self._loan_list = loan_list

    @property
    def loan_list(self):
        return self._loan_list

    def totalBeginingBalance(self):
        balance = sum(loan.current_balance for loan in self._loan_list)
        return balance

    def totalOriginalBalance(self):
        origBalance = sum(loan.original_amount for loan in self._loan_list)
        return origBalance

    def WAC_begining(self):
        intProdBal = sum(loan.current_balance * loan._rate for loan in self._loan_list)
        WAC = intProdBal / self.totalBeginingBalance()
        return WAC

    def WADuration(self):
        termProdBal = sum(loan.current_balance * loan.term for loan in self._loan_list)
        WADuration = termProdBal / self.totalBeginingBalance()
        return WADuration

    def numOfActive_period(self, period):
        count = len([loan for loan in self._loan_list if loan.getBalance(period) > 0])
        return count

    def balance_period(self, period):
        balance = sum(loan.getBalance(period) for loan in self._loan_list)
        return balance

    def payment_period(self, period):
        payment = sum(loan.getPayment(period) for loan in self._loan_list)
        return payment

    def intPayment_period(self, period):
        intPayment = sum(loan.getIntPayment(period) for loan in self._loan_list)
        return intPayment

    def priPayment_period(self, period):
        prinPayment = sum(loan.getPrinciplePayment(period) for loan in self._loan_list)
        return prinPayment

    def curtailment_period(self, period):
        curtailment = sum(loan.getCurtailmentPayment(period) for loan in self._loan_list)
        return curtailment

    def chargeOffPrin_period(self, period):
        chargeOffPrin = sum(loan.getChargeOff_prin(period) for loan in self._loan_list)
        return chargeOffPrin

    def chargeOffInt_period(self, period):
        chargeOffInt = sum(loan.getChargeOff_int(period) for loan in self._loan_list)
        return chargeOffInt

    def __iter__(self):
        return iter(self._loan_list)

    # run simulation for the period, must be run from period = 1
    def checkStatus(self, period):
        # run each loan in the pool
        for loan in self._loan_list:
            rand_num = np.random.uniform(0, 1)
            loan.checkStatus(rand_num, period)
            _ = loan.make_monthly_payment(period)
            _ = loan.make_interest_payment(period)
            _ = loan.make_prin_payment(period)
            _ = loan.calc_balance(period)
        return self.numOfActive_period(period)

    # reset every loan to period = 0 status, this function is for simulation
    def restLoanPool(self):
        for loan in self._loan_list:
            loan.reset()
