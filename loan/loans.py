from .loan_base import Loan


# Fixed rate loan class derived from Loan class
class FixedRateLoan(Loan):
    def rate(self, period):
        return self._rate


# Variable rate loan class derived from Loan class
class VariableRateLoan(Loan):
    def __init__(self, loan_id, term,
                 original_amount,
                 current_balance,
                 current_seasoning,
                 current_status,
                 credit_attributes,
                 rate_dict,
                 dq_to_default_months=3):
        self._rateDict = rate_dict
        super(VariableRateLoan, self).__init__(loan_id, term, None,
                                               original_amount,
                                               current_balance,
                                               current_seasoning,
                                               current_status,
                                               credit_attributes,
                                               dq_to_default_months)
    def rate(self, period):
        rate = self._rateDict[min(self._rateDict.keys())]
        rate_change_time = sorted(self._rateDict.keys())

        for next_rate_change_time in rate_change_time:
            if self._current_seasoning + period < next_rate_change_time:
                break
            rate = self._rateDict[next_rate_change_time]
        return rate
