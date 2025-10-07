import util, math, random
from collections import defaultdict
from util import ValueIteration

############################################################
# Problem 2.2

# If you decide 2.2 is true, prove it in your submission and put "return None" for
# the code blocks below.  If you decide that 2.2 is false, construct a counterexample.
class CounterexampleMDP(util.MDP):
    # Return a value of any type capturing the start state of the MDP.
    def startState(self):
        # BEGIN_YOUR_CODE 
        raise Exception("Not implemented yet")
        # END_YOUR_CODE

    # Return a list of strings representing actions possible from |state|.
    def actions(self, state):
        # BEGIN_YOUR_CODE 
        raise Exception("Not implemented yet")
        # END_YOUR_CODE

    # Given a |state| and |action|, return a list of (newState, prob, reward) tuples
    # corresponding to the states reachable from |state| when taking |action|.
    # Remember that if |state| is an end state, you should return an empty list [].
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE 
        raise Exception("Not implemented yet")
        # END_YOUR_CODE

    # Set the discount factor (float or integer) for your counterexample MDP.
    def discount(self):
        # BEGIN_YOUR_CODE 
        raise Exception("Not implemented yet")
        # END_YOUR_CODE

############################################################
# Problem 3

class BlackjackMDP(util.MDP):
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: list of integers (face values for each card included in the deck)
        multiplicity: single integer representing the number of cards with each face value
        threshold: maximum number of points (i.e. sum of card values in hand) before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    # Return the start state.
    # Look closely at this function to see an example of state representation for our Blackjack game.
    # Each state is a tuple with 3 elements:
    #   -- The first element of the tuple is the sum of the cards in the player's hand.
    #   -- If the player's last action was to peek, the second element is the index
    #      (not the face value) of the next card that will be drawn; otherwise, the
    #      second element is None.
    #   -- The third element is a tuple giving counts for each of the cards remaining
    #      in the deck, or None if the deck is empty or the game is over (e.g. when
    #      the user quits or goes bust).
    def startState(self):
        return (0, None, (self.multiplicity,) * len(self.cardValues))

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be placed into the succAndProbReward function below.
    def actions(self, state):
        return ['Take', 'Peek', 'Quit']

    # Given a |state| and |action|, return a list of (newState, prob, reward) tuples
    # corresponding to the states reachable from |state| when taking |action|.
    # A few reminders:
    # * Indicate a terminal state (after quitting, busting, or running out of cards)
    #   by setting the deck to None.
    # * If |state| is an end state, you should return an empty list [].
    # * When the probability is 0 for a transition to a particular new state,
    #   don't include that state in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE 
        total, peekIndex, deckCounts = state

        # If state is terminal (deckCounts is None), no successors
        if deckCounts is None:
            return []

        # Helper to check if deck becomes empty after removal
        def remove_one(counts, idx):
            countsList = list(counts)
            countsList[idx] -= 1
            return tuple(countsList)

        results = []

        if action == 'Quit':
            # Quit ends the game: terminal with reward equal to current total
            results.append(((total, None, None), 1, total))
            return results

        if action == 'Peek':
            # Cannot peek twice in a row
            if peekIndex is not None:
                return []
            remaining = sum(deckCounts)
            if remaining == 0:
                # Should not happen since terminal decks should be None, but guard anyway
                return []
            for i, cnt in enumerate(deckCounts):
                if cnt == 0:
                    continue
                prob = cnt / float(remaining)
                # After peeking, we know next card index but do not change deck
                results.append(((total, i, deckCounts), prob, -self.peekCost))
            return results

        if action == 'Take':
            # If previously peeked, forced to draw that specific card
            if peekIndex is not None:
                cardValue = self.cardValues[peekIndex]
                newTotal = total + cardValue
                newDeckCounts = remove_one(deckCounts, peekIndex)
                # Bust check
                if newTotal > self.threshold:
                    results.append(((newTotal, None, None), 1, 0))
                    return results
                # Deck empty -> terminal with reward equal to newTotal
                if sum(newDeckCounts) == 0:
                    results.append(((newTotal, None, None), 1, newTotal))
                    return results
                # Otherwise continue, clearing peek flag
                results.append(((newTotal, None, newDeckCounts), 1, 0))
                return results

            # No peek: draw according to counts
            remaining = sum(deckCounts)
            if remaining == 0:
                # Should be terminal already, but guard
                return []
            for i, cnt in enumerate(deckCounts):
                if cnt == 0:
                    continue
                prob = cnt / float(remaining)
                cardValue = self.cardValues[i]
                newTotal = total + cardValue
                newDeckCounts = remove_one(deckCounts, i)
                if newTotal > self.threshold:
                    results.append(((newTotal, None, None), prob, 0))
                else:
                    if sum(newDeckCounts) == 0:
                        # Deck exhausted without bust -> terminal with reward newTotal
                        results.append(((newTotal, None, None), prob, newTotal))
                    else:
                        # Continue game
                        results.append(((newTotal, None, newDeckCounts), prob, 0))
            return results

        # Unknown action
        return []
        # END_YOUR_CODE

    def discount(self):
        return 1

############################################################
# Problem 3b

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the
    optimal action at least 10% of the time.
    """
    # BEGIN_YOUR_CODE 
    # Design: A deck with many safe small cards and some large bust cards,
    # so paying peekCost=1 to decide whether to take or quit is valuable
    # when current total is near threshold=20.
    # Example: values [1, 11] with moderate multiplicity tends to make peeking
    # optimal in many near-threshold states.
    return BlackjackMDP(cardValues=[1, 11], multiplicity=4, threshold=20, peekCost=1)
    # END_YOUR_CODE