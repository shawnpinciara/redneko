# Write your code here :-)
class Btn:
    def __init__(self):
        self._current = 0
        self._prev = 0
    def set_prev(self,el):
        self._prev = el
    def set_current(self,el):
        self._current = el
    def get_prev(self):
        return self._prev
    def get_current(self):
        return self._current
