class PlayerLostException(Exception):
    '''
    Raised when a player loses by not providing valid input within the time limit or by providing an invalid format.
    '''
    def __init__(self, first: bool, second: bool, first_error_message: str|None = None, second_error_message: str|None = None) -> None:
        self.first = first
        self.second = second
        self.first_error_message = first_error_message
        self.second_error_message = second_error_message