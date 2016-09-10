from copy import deepcopy


class Factory:
    pass


class ProfileMessage():
    def __init__(self, msg, previous):
        self.previous = deepcopy(previous)
        self.msg = deepcopy(msg)
