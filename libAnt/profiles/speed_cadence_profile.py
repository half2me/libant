from libAnt.profiles.factory import ProfileMessage


class SpeedAndCadenceProfileMessage(ProfileMessage):
    """ Message from Speed & Cadence sensor """

    def __init__(self, msg, previous, staleSpeedCounter, staleCadenceCounter):
        super().__init__(msg, previous)
        self.staleSpeedCounter = staleSpeedCounter
        self.staleCadenceCounter = staleCadenceCounter

        if self.previous is not None:
            if self.speedEventTime == self.previous.speedEventTime:
                self.staleSpeedCount[0] += 1
            else:
                self.staleSpeedCount[0] = 0

            if self.cadenceEventTime == self.previous.cadenceEventTime:
                self.staleCadenceCount[0] += 1
            else:
                self.staleCadenceCount[0] = 0

    maxCadenceEventTime = 65536
    maxSpeedEventTime = 65536
    maxSpeedRevCount = 65536
    maxCadenceRevCount = 65536
    maxStaleSpeedCount = 7
    maxStaleCadenceCount = 7

    @lazyproperty
    def cadenceEventTime(self):
        """ Represents the time of the last valid bike cadence event (1/1024 sec) """
        return (self.raw[2] << 8) | self.raw[1]

    @lazyproperty
    def cumulativeCadenceRevolutionCount(self):
        """ Represents the total number of pedal revolutions """
        return (self.raw[4] << 8) | self.raw[3]

    @lazyproperty
    def speedEventTime(self):
        """ Represents the time of the last valid bike speed event (1/1024 sec) """
        return (self.raw[6] << 8) | self.raw[5]

    @lazyproperty
    def cumulativeSpeedRevolutionCount(self):
        """ Represents the total number of wheel revolutions """
        return (self.raw[8] << 8) | self.raw[7]

    @lazyproperty
    def speedEventTimeDiff(self):
        if self.previous is None:
            return 0
        elif self.speedEventTime < self.previous.speedEventTime:
            # Rollover
            return (self.speedEventTime - self.previous.speedEventTime) + self.maxSpeedEventTime
        else:
            return self.speedEventTime - self.previous.speedEventTime

    @lazyproperty
    def cadenceEventTimeDiff(self):
        if self.previous is None:
            return 0
        elif self.cadenceEventTime < self.previous.cadenceEventTime:
            # Rollover
            return (self.cadenceEventTime - self.previous.cadenceEventTime) + self.maxCadenceEventTime
        else:
            return self.cadenceEventTime - self.previous.cadenceEventTime

    @lazyproperty
    def speedRevCountDiff(self):
        if self.previous is None:
            return None
        elif self.cumulativeSpeedRevolutionCount < self.previous.cumulativeSpeedRevolutionCount:
            # Rollover
            return (
                       self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount) + self.maxSpeedRevCount
        else:
            return self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount

    @lazyproperty
    def cadenceRevCountDiff(self):
        if self.previous is None:
            return None
        elif self.cumulativeCadenceRevolutionCount < self.previous.cumulativeCadenceRevolutionCount:
            # Rollover
            return (
                       self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount) + self.maxCadenceRevCount
        else:
            return self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount

    def speed(self, c):
        """
        :param c: circumference of the wheel (mm)
        :return: The current speed (m/sec)
        """
        if self.previous is None:
            return 0
        if self.speedEventTime == self.previous.speedEventTime:
            if self.staleSpeedCount[0] > self.maxStaleSpeedCount:
                return 0
            return self.previous.speed(c)
        return self.speedRevCountDiff * 1.024 * c / self.speedEventTimeDiff

    @lazyproperty
    def cadence(self):
        """
        :return: RPM
        """
        if self.previous is None:
            return 0
        if self.cadenceEventTime == self.previous.cadenceEventTime:
            if self.staleCadenceCount[0] > self.maxStaleCadenceCount:
                return 0
            return self.previous.cadence
        return self.cadenceRevCountDiff * 1024 * 60 / self.cadenceEventTimeDiff
