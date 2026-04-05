class PlayerLostException(Exception):
    '''
    Raised when a player loses by not providing valid input within the time limit or by providing an invalid format.
    '''
    def __init__(self, first: bool, second: bool):
        self.first = first
        self.second = second