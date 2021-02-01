from product.vote_calc import VoteCalc
from utils import flat_map


class TotalAmountPurchasedVoteCalc(VoteCalc):

    def _get_multiplier(self, user):
        return len(flat_map(lambda order: order.snapshots, user.orders)) + 1