from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class SpeedAndCadenceProfileMessage(ProfileMessage):
    """ Message from Speed & Cadence sensor """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.staleSpeedCounter = previous.staleSpeedCounter if previous is not None else 0
        self.staleCadenceCounter = previous.staleCadenceCounter if previous is not None else 0

        if self.previous is not None:
            if self.speedEventTime == self.previous.speedEventTime:
                self.staleSpeedCounter += 1
            else:
                self.staleSpeedCounter = 0

            if self.cadenceEventTime == self.previous.cadenceEventTime:
                self.staleCadenceCounter += 1
            else:
                self.staleCadenceCounter = 0

    maxCadenceEventTime = 65536
    maxSpeedEventTime = 65536
    maxSpeedRevCount = 65536
    maxCadenceRevCount = 65536
    maxstaleSpeedCounter = 7
    maxstaleCadenceCounter = 7

    def __str__(self):
        return super().__str__() + ' Speed: ' + str(self.speed(2096)) + ' Cadence: ' + str(self.cadence)

    @lazyproperty
    def cadenceEventTime(self):
        """ Represents the time of the last valid bike cadence event (1/1024 sec) """
        return (self.msg.content[1] << 8) | self.msg.content[0]

    @lazyproperty
    def cumulativeCadenceRevolutionCount(self):
        """ Represents the total number of pedal revolutions """
        return (self.msg.content[3] << 8) | self.msg.content[2]

    @lazyproperty
    def speedEventTime(self):
        """ Represents the time of the last valid bike speed event (1/1024 sec) """
        return (self.msg.content[5] << 8) | self.msg.content[4]

    @lazyproperty
    def cumulativeSpeedRevolutionCount(self):
        """ Represents the total number of wheel revolutions """
        return (self.msg.content[7] << 8) | self.msg.content[6]

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
            if self.staleSpeedCounter > self.maxstaleSpeedCounter:
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
            if self.staleCadenceCounter > self.maxstaleCadenceCounter:
                return 0
            return self.previous.cadence
        return self.cadenceRevCountDiff * 1024 * 60 / self.cadenceEventTimeDiff
