# Write your code here :-)
class Pattern:
    def __init__(self):
        self._pattern = [0,0,0,0,0,0,0,0]
    def set(self,i,el):
        self._pattern[i] = el
    def get(self,i):
        return self._pattern[i]
    def set_array(self,array):
        self._pattern = array
