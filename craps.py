import random

''' Define bets and their associated is_valid and get_payout functions here '''
def pass_is_valid(self, bet):
    ''' Only bet pass if we're at the start of a round '''
    return self.point == 0 and not self.round_is_over
def pass_get_payout(self, bet):
    if not self.round_is_over:
        raise RuntimeError('''Don't pay out unless round is over!''')
    if self.point == 0 and (self.last_roll == 7 or self.last_roll == 11):
        return 2*bet.amount
    elif self.point == self.last_roll:
        return 2*bet.amount
    else:
        return 0
    
bets = {
    'pass' : {'is_valid': pass_is_valid, 'get_payout': pass_get_payout}
    }

class Log:
    def __init__(self):
        self.num_rounds = 0         # Maintained in Player.make_bets()
        self.num_rolls = 0          # Maintained in Player.make_bets()
        self.num_bets = 0           # Maintained in Player.make_bets()
        self.winnings_history = []  # Maintained in Player.get_payouts()

    def __repr__(self):
        if self.winnings_history:
            return '<Log #rounds:%s #rolls:%s #bets:%s winnings:%s>' % \
               (self.num_rounds, self.num_rolls, self.num_bets,
                self.winnings_history[:-1])
        else:
            return '<Log #rounds:%s #rolls:%s #bets:%s winnings:0>' % \
               (self.num_rounds, self.num_rolls, self.num_bets)

class Bet:
    def __init__(self, bet_type, amount):
        if amount <= 0:
            raise ValueError('Bet amount must be positive')
        self.bet_type = bet_type
        self.amount = amount

    def __repr__(self):
        return '<Bet ' + self.bet_type + ' amount:%s>' % self.amount

class Status:
    # Use a point of 0 to denote an unset point
    acceptable_points = [0, 4, 5, 6, 8, 9, 10]
    
    def __init__(self, min_bet, round_is_over, point, point_just_set):
        if point not in self.acceptable_points:
            raise ValueError('Unacceptable point set: ' + str(point))
        if min_bet <= 0:
            raise ValueError('Min bet must be positive')
        self.min_bet = min_bet
        self.round_is_over = round_is_over
        self.point = point
        self.point_just_set = point_just_set

    def __repr__(self):
        return '<Status min_bet:%s rnd_ovr:%s point:%s>' % (self.min_bet,
                                                            self.round_is_over,
                                                            self.point)

class Board:

    def __init__(self, min_bet=5):
        if min_bet <= 0:
            raise ValueError('Min bet must be positive')
        self.min_bet = min_bet
        self.reset()
    
    def roll(self, fixed_roll=None):
        if fixed_roll:
            self.last_roll = fixed_roll
        else:
            dice1 = random.randint(1,6)
            dice2 = random.randint(1,6)
            self.last_roll = dice1 + dice2

        if self.point == 0 and self.last_roll in [4,5,6,8,9,10]:
            self.point = self.last_roll
            self.point_just_set = True
        elif self.point_just_set:
            self.point_just_set = False

        ''' Update board status '''
        if not self.point_just_set:
            self.round_is_over = self.last_roll in [2, 3, 7, 11, 12, self.point]
        
        return self.last_roll

    def take_bets(self, bets):
        for bet in bets:
            if not self.bet_validator(bet):
                raise ValueError('Bet ' + str(bet) + ' not valid!')
            self.bets.append(bet)

    def return_payouts(self):
        payouts = []
        for bet in self.bets:
            payouts.append(bets[bet.bet_type]['get_payout'](self, bet))
        self.reset()
        return payouts

    def get_status(self):
        return Status(self.min_bet, self.round_is_over, self.point,
                      self.point_just_set)

    def reset(self):
        self.bets = []
        self.round_is_over = False
        self.point = 0
        self.point_just_set = False
        self.last_roll = 0
        return self.get_status()

    def bet_validator(self, bet):
        
        if bet.amount < self.min_bet:
            raise ValueError('Bet must be larger than min bet!')
        if not bet.bet_type in bets:
            raise NotImplementedError(
                'Bet ' + bet.bet_type + ' not implemented')
        return bets[bet.bet_type]['is_valid'](self, bet)
            


class Player:

    def __init__(self, betting_strategy, quitting_strategy):
        self.betting_strategy = betting_strategy
        self.quitting_strategy = quitting_strategy
        self.log = Log()
        self.winnings = 0

    def is_quitting(self):
        return self.quitting_strategy(self)

    def make_bets(self, board_status):

        ''' Increment the num_rounds at the start of each round '''
        if board_status.point == 0 and not board_status.round_is_over:
            self.log.num_rounds = self.log.num_rounds + 1

        ''' Increment the num_rolls before each roll '''
        if not board_status.round_is_over:
            self.log.num_rolls = self.log.num_rolls + 1
        
        new_bets = self.betting_strategy(self, board_status)

        ''' Increment the num_bets '''
        self.log.num_bets = self.log.num_bets + len(new_bets)

        return new_bets

    def get_payouts(self, payouts):
        self.winnings = self.winnings + sum(payouts)
        self.log.winnings_history.append(self.winnings)

'''-----------------------------------------------------------------------------
---  Quitting strategies below!                                              ---
-----------------------------------------------------------------------------'''
def always_quits(self):
    return True
def quits_after_one(self):
    if self.log.num_rounds >= 1:
        return True
    else:
        return False
def quits_after_ten(self):
    if self.log.num_rounds >= 10:
        return True
    else:
        return False

'''-----------------------------------------------------------------------------
---  Betting strategies below!                                               ---
-----------------------------------------------------------------------------'''
def bets_nothing(self, board_status):
    return []
def bets_pass(self, board_status):
    if board_status.point == 0 and not board_status.round_is_over:
        self.winnings = self.winnings - board_status.min_bet
        return [Bet('pass',board_status.min_bet)]
    else:
        return []

