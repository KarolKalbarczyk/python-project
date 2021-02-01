import math

from product.vote_calc import VoteCalc
from datetime import date

class MembershipPeriodVoteCalc(VoteCalc):

    def _get_multiplier(self, user):
        joinDate = user.joinDate
        currentDate = date.today()
        return math.sqrt((currentDate - joinDate).days) + 1