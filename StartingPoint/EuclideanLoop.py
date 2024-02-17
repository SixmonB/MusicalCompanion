# Author : Pierre De Loor
# Date : 01/09/2022

import math

class EuclideanLoop :
    def __init__(self, step, onset, shift) :
        assert onset < step
        assert shift < step
        self._step = step
        self._onset = onset
        self._shift = shift
        self._sequence = []
        self.computeSequence()
    
    def _rotate(self, n):
        self._sequence = self._sequence[n:] + self._sequence[:n]
    
    def computeSequence(self) :
        offset = self._step/self._onset
        listTick = []
        currentTime = 0
        for i in range(0,self._onset) :
            listTick.append(currentTime)
            currentTime = currentTime + offset
        listTickAlign = []
        for i in listTick :
            listTickAlign.append(round(i))
        listTickOnStep = []
        for i in range(0,self._step) :
            if i in listTickAlign :
                self._sequence.append(1)
            else :
                self._sequence.append(0)
        self._rotate(self._shift)

    

    def getSequence(self) :
        return self._sequence


if __name__ == "__main__" :
    el = EuclideanLoop(12, 5, 0)
    print("Loop : ", el.getSequence())











    

