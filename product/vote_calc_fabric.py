from product import vote_calc
from product.membership_period_vote_calc import MembershipPeriodVoteCalc
from product.total_amount_purchased_vote_calc import TotalAmountPurchasedVoteCalc


def get_calculator() -> vote_calc:
    return MembershipPeriodVoteCalc(TotalAmountPurchasedVoteCalc())