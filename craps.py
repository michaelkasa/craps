''' Craps simulator module.

This module allows for simulations of different craps betting strategies.
'''

__free_odds__ = {4: {'num':2.,'den':1.},
                 5: {'num':3.,'den':2.},
                 6: {'num':6.,'den':5.},
                 8: {'num':6.,'den':5.},
                 9: {'num':3.,'den':2.},
                 10:{'num':2.,'den':1.}}

import random


def pass_is_valid(self, bet):
    ''' Pass bet is valid only at the start of the round '''
    return self.point == 0 and not self.round_is_over

def pass_get_payout(self, bet):
    ''' The pass bet pays one-to-one.

    The pass bet wins with an initial roll of 7 or 11; it also wins if
    the point is set, then rolled again before a 7.
    '''
    if not self.round_is_over:
        raise RuntimeError("Don't pay out unless round is over!")
    if self.point == 0 and (self.last_roll == 7 or self.last_roll == 11):
        return 2*bet.amount
    elif self.point == self.last_roll:
        return 2*bet.amount
    else:
        return 0

def pass_odds_is_valid(self, bet):
    ''' Pass odds bet is valid once the point is set '''
    return not self.round_is_over and self.point > 0

def pass_odds_get_payout(self, bet):
    ''' Pass odds pay out true odds

    By true odds, we mean 2:1 for 4 or 10, 3:2 for 5 or 9, and 6:5 for
    6 or 8.
    '''
    if not self.round_is_over:
        raise RuntimeError('''Don't pay out unless round is over!''')
    if self.point > 0 and self.last_roll == self.point:
        return bet.amount * (1 + __free_odds__[self.point]['num']/
                             __free_odds__[self.point]['den'])
    else:
        return 0

def bets_nothing(self, board_status):
    ''' Bet nothing '''
    return []

def bets_pass(self, board_status):
    ''' Bet pass at the start of each round '''
    if board_status.point == 0 and not board_status.round_is_over:
        self.winnings = self.winnings - board_status.min_bet
        return [Bet('pass',board_status.min_bet)]
    else:
        return []
    
def bets_pass_and_odds(self, board_status):
    ''' Take the free odds after the point is set '''
    if board_status.point == 0 and not board_status.round_is_over:
        self.winnings = self.winnings - board_status.min_bet
        return [Bet('pass',board_status.min_bet)]
    elif board_status.point_just_set:
        bet_amount = board_status.min_bet + \
                     (board_status.min_bet % \
                      __free_odds__[board_status.point]['den'])
        self.winnings = self.winnings - bet_amount
        return [Bet('pass_odds',bet_amount)]
    else:
        return []

def always_quits(self):
    ''' Always quit '''
    return True

def quits_after_one(self):
    ''' Quit after a single hand '''
    return self.log.num_rounds >= 1

def quits_after_N_rounds(self):
    ''' Quit after N hands '''
    return self.log.num_rounds >= self.N

def quits_after_gain_or_lose_50(self):
    ''' Quit after gaining or losing 50 '''
    return self.log.winnings_history and \
           abs(self.log.winnings_history[-1]) >= 50
    
def quits_after_gainG_or_lossL_or_roundMax(self):
    ''' The function name is self-explanatory '''
    return self.log.winnings_history and \
           (self.log.winnings_history[-1] <= -abs(self.lossL) or \
           self.log.winnings_history[-1] >= self.gainG or \
           self.log.num_rounds >= self.roundMax)


class Log:
    ''' The Log class provides data about the player '''
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
    ''' The Bet class provides a common structure for bets '''    
    # List of supported bets; each has a 'is_valid' and 'get_payout'
    # function.
    __bets__ = {'pass' :      {'is_valid': pass_is_valid,
                               'get_payout': pass_get_payout     },
                'pass_odds' : {'is_valid': pass_odds_is_valid,
                               'get_payout': pass_odds_get_payout}
    }
    
    def __init__(self, bet_type, amount):
        if amount <= 0:
            raise ValueError('Bet amount must be positive')
        self.bet_type = bet_type
        self.amount = amount

    def __repr__(self):
        return '<Bet ' + self.bet_type + ' amount:%s>' % self.amount

class Status:
    ''' The Status class provides information about the board '''    
    def __init__(self, min_bet, round_is_over, point, point_just_set):
        if point not in Board.__acceptable_points__:
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
    ''' The Board class runs the craps board '''
    # Use a point of 0 to denote an unset point
    __acceptable_points__ = [0, 4, 5, 6, 8, 9, 10]
    
    def __init__(self, min_bet=5):
        if min_bet <= 0:
            raise ValueError('Min bet must be positive')
        self.min_bet = min_bet
        self.reset()
    
    def roll(self, fixed_roll=None):
        ''' Roll the dice at the craps board.

        If an input is provided, the board acts as if this number is
        rolled -- this feature is useful for debugging.
        '''
        # Get roll
        if fixed_roll:
            self.last_roll = fixed_roll
        else:
            dice1 = random.randint(1,6)
            dice2 = random.randint(1,6)
            self.last_roll = dice1 + dice2
            
        # Set the point
        if self.point == 0 and self.last_roll in [4,5,6,8,9,10]:
            self.point = self.last_roll
            self.point_just_set = True
        elif self.point_just_set:
            self.point_just_set = False

        # Determine if the round is over
        if self.point == 0:
            self.round_is_over = self.last_roll in [2, 3, 7, 11, 12]
        elif not self.point_just_set:
            self.round_is_over = self.last_roll in [7, self.point]
        return self.last_roll

    def take_bets(self, bets):
        ''' Take bets from the user

        Bets are validated using their bet_validator function, then
        appended to the list of bets.
        '''
        for bet in bets:
            if not self.bet_validator(bet):
                raise ValueError('Bet ' + str(bet) + ' not valid!')
            self.bets.append(bet)

    def return_payouts(self):
        ''' Return bets to the user, according to their get_payout functions '''
        payouts = []
        for bet in self.bets:
            payouts.append(Bet.__bets__[bet.bet_type]['get_payout'](self, bet))
        self.reset()
        return payouts

    def get_status(self):
        ''' Return Status class '''
        return Status(self.min_bet, self.round_is_over, self.point,
                      self.point_just_set)

    def reset(self):
        ''' Reset the board to its initial state '''
        self.bets = []
        self.round_is_over = False
        self.point = 0
        self.point_just_set = False
        self.last_roll = 0
        return self.get_status()

    def bet_validator(self, bet):
        ''' Validate that the bet is legal using its is_valid function '''
        if bet.amount < self.min_bet:
            raise ValueError('Bet must be larger than min bet!')
        if not bet.bet_type in Bet.__bets__:
            raise NotImplementedError(
                'Bet ' + bet.bet_type + ' not implemented')
        return Bet.__bets__[bet.bet_type]['is_valid'](self, bet)
            

class Player:
    ''' The Player class control's a craps bettor's actions '''
    def __init__(self, betting_strategy, quitting_strategy):
        self.betting_strategy = betting_strategy
        self.quitting_strategy = quitting_strategy
        self.log = Log()
        self.winnings = 0

    def is_quitting(self):
        ''' Determine if the player is quitting '''
        return self.quitting_strategy(self)

    def make_bets(self, board_status):
        ''' Make the player's bets '''
        # Increment the num_rounds at the start of each round 
        if board_status.point == 0 and not board_status.round_is_over:
            self.log.num_rounds = self.log.num_rounds + 1
        # Increment the num_rolls before each roll
        if not board_status.round_is_over:
            self.log.num_rolls = self.log.num_rolls + 1
        new_bets = self.betting_strategy(self, board_status)
        # Increment the num_bets
        self.log.num_bets = self.log.num_bets + len(new_bets)
        return new_bets

    def get_payouts(self, payouts):
        ''' Collect payouts from the board '''
        self.winnings = self.winnings + sum(payouts)
        self.log.winnings_history.append(self.winnings)

