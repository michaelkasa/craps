import unittest
import random

from craps import *

class TestBetMethods(unittest.TestCase):

    ''' Test exception raised when bet amount is nonpositive '''
    def test_bet_amount_exceptions(self):

        with self.assertRaises(ValueError):
            Bet('pass',0)
        with self.assertRaises(ValueError):
            Bet('pass',-20)

class TestBoardMethods(unittest.TestCase):

    ''' Test roll() in the board '''
    def test_roll(self):

        ''' For 100 rolls, make sure we always get something allowed '''
        b = Board()
        allowed_rolls = [2,3,4,5,6,7,8,9,10,11,12]
        for ii in range(100):
            self.assertIn(b.roll(),allowed_rolls)

        ''' Test all the numbers show up when we roll 1000 times '''
        rolls = []
        for ii in range(1000):
            rolls.append(b.roll())
        rolls = set(rolls)
        for allowed_roll in allowed_rolls:
            self.assertIn(allowed_roll, rolls)

    def test_min_bet_exception(self):
        with self.assertRaises(ValueError):
            b = Board(-5)
        with self.assertRaises(ValueError):
            b = Board(0)

class TestStatusMethods(unittest.TestCase):

    ''' Test exception raised when point is invalid '''
    def test_point_exception(self):
        for bad_point in [1,2,3,7,11,12,-2]:
            with self.assertRaises(ValueError):
                s = Status(5, False, 1, False)

    def test_min_bet_exception(self):
        for bad_bet in range(-100,1):
            with self.assertRaises(ValueError):
                s = Status(bad_bet, False, 6, False)

class TestPlayerMethods(unittest.TestCase):

    def test_quitting_strategy(self):
        quitter = Player(bets_nothing, always_quits)
        self.assertTrue(quitter.is_quitting())

    def test_betting_strategy(self):
        board_status = Status(5,False,0,False)
        bets_nothing_dude = Player(bets_nothing, always_quits)

        # AssertFalse here actually asserts the list is empty
        self.assertFalse(bets_nothing_dude.make_bets(board_status))

    def test_print_log(self):
        player = Player(bets_nothing, always_quits)
        self.assertEqual('<Log #rounds:0 #rolls:0 #bets:0 winnings:0>',
                         str(player.log))

class TestBets(unittest.TestCase):
    
    def test_bets_nothing_fn(self):
        player = Player(bets_nothing, always_quits)
        board_status = Status(5, False, 0, False)
        self.assertFalse(bets_nothing(player,board_status))

    def test_bets_pass_fn(self):
        player = Player(bets_pass, always_quits)
        board_status = Status(5, False, 0, False)
        pass_bet = bets_pass(player, board_status)
        self.assertEqual(len(pass_bet),1)
        self.assertEqual(pass_bet[0].bet_type,'pass')
        self.assertEqual(pass_bet[0].amount,board_status.min_bet)

    def test_bets_nothing(self):
        player = Player(bets_nothing, quits_after_one)
        board_status = Status(5, False, 0, False)
        self.assertFalse(player.make_bets(board_status))

    def test_bets_pass(self):
        player = Player(bets_pass, always_quits)
        board_status = Status(5, False, 0, False)
        pass_bet = player.make_bets(board_status)
        self.assertEqual(len(pass_bet),1)
        self.assertEqual(pass_bet[0].bet_type,'pass')
        self.assertEqual(pass_bet[0].amount,board_status.min_bet)

    def test_always_quits_fn(self):
        player = Player(bets_pass, always_quits)
        self.assertTrue(always_quits(player))

    def test_always_quits(self):
        player = Player(bets_pass, always_quits)
        self.assertTrue(player.is_quitting())

    def test_quits_after_one(self):
        board = Board()
        player = Player(bets_pass, quits_after_one)
        initial_status = board.get_status()
        first_bet = player.make_bets(initial_status)
        self.assertTrue(first_bet)
        
        board.roll(7)  # End the first round here
        second_bet = player.make_bets(board.get_status())
        self.assertFalse(second_bet)

class TestLogging(unittest.TestCase):

    def test_winning_one_pass(self):
        player = Player(bets_pass, quits_after_one)
        self.assertEqual(player.winnings, 0)
        board = Board()
        board.take_bets(player.make_bets(board.get_status()))
        board.roll(7)
        self.assertTrue(board.round_is_over)
        player.get_payouts(board.return_payouts())
        self.assertEqual(player.log.winnings_history[-1],5)
        self.assertEqual(player.winnings, 5)

class TestFullScenario(unittest.TestCase):

    def test_pass_winning_a_lot(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([7,11])
            board.roll(roll)
            player.get_payouts(board.return_payouts())
        self.assertEqual(player.winnings, 50)
        self.assertEqual(player.log.winnings_history,[x for x in range(5,51,5)])

    def test_pass_winning_a_lot_by_points(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            ''' Roll 1, set the point '''
            board.reset()
            self.assertFalse(board.round_is_over)
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([4,5,6,8,9,10])
            board.roll(roll)

            ''' Roll 2, hit the point '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            board.roll(roll)
            self.assertTrue(board.round_is_over)
            player.get_payouts(board.return_payouts())
            
        self.assertEqual(player.winnings, 50)
        self.assertEqual(player.log.winnings_history,[x for x in range(5,51,5)])        

    def test_pass_winning_a_lot_by_points_with_empty_rolls(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            ''' Roll 1, set the point '''
            board.reset()
            self.assertFalse(board.round_is_over)
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([4,5,6,8,9,10])
            board.roll(roll)

            ''' Roll 2, hit another point (nothing happens) '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            other_points = [4,5,6,8,9,10]
            other_points.remove(roll)
            another_point = random.choice(other_points)
            board.roll(another_point)

            ''' Roll 3, hit the point '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            board.roll(roll)
            self.assertTrue(board.round_is_over)
            player.get_payouts(board.return_payouts())
            
        self.assertEqual(player.winnings, 50)
        self.assertEqual(player.log.winnings_history,[x for x in range(5,51,5)])

    def test_pass_losing_a_lot(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([2,3,12])
            board.roll(roll)
            player.get_payouts(board.return_payouts())
        self.assertEqual(player.winnings, -50)
        self.assertEqual(player.log.winnings_history,[x for x in range(-5,-51,-5)])

    def test_pass_losing_a_lot_by_points(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            ''' Roll 1, set the point '''
            board.reset()
            self.assertFalse(board.round_is_over)
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([4,5,6,8,9,10])
            board.roll(roll)

            ''' Roll 2, it's a 7 -- sad! '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            board.roll(7)
            self.assertTrue(board.round_is_over)
            player.get_payouts(board.return_payouts())
            
        self.assertEqual(player.winnings, -50)
        self.assertEqual(player.log.winnings_history,[x for x in range(-5,-51,-5)])

    def test_pass_losing_a_lot_by_points_with_empty_rolls(self):
        player = Player(bets_pass, quits_after_ten)
        board = Board()

        while not player.is_quitting():
            ''' Roll 1, set the point '''
            board.reset()
            self.assertFalse(board.round_is_over)
            board.take_bets(player.make_bets(board.get_status()))
            roll = random.choice([4,5,6,8,9,10])
            board.roll(roll)

            ''' Roll 2, hit another point (nothing happens) '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            other_points = [4,5,6,8,9,10]
            other_points.remove(roll)
            another_point = random.choice(other_points)
            board.roll(another_point)

            ''' Roll 3, it's a 7 -- sad! '''
            self.assertFalse(board.round_is_over)
            new_bets = player.make_bets(board.get_status())
            self.assertFalse(new_bets)
            board.take_bets(new_bets)
            board.roll(7)
            self.assertTrue(board.round_is_over)
            player.get_payouts(board.return_payouts())
            
        self.assertEqual(player.winnings, -50)
        self.assertEqual(player.log.winnings_history,[x for x in range(-5,-51,-5)])

if __name__ == '__main__':
    unittest.main()
    
