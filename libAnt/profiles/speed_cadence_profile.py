from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class SpeedAndCadenceProfileMessage(ProfileMessage):
    """ Message from Speed & Cadence sensor """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)
        self.staleSpeedCounter = previous.staleSpeedCounter if previous is not None else 0
        self.staleCadenceCounter = previous.staleCadenceCounter if previous is not None else 0
        self.totalRevolutions = previous.totalRevolutions + self.cadenceRevCountDiff if previous is not None else 0
        self.totalSpeedRevolutions = previous.totalSpeedRevolutions + self.speedRevCountDiff if previous is not None else 0

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
        ret = '{} Speed: {:.2f}m/s (avg: {:.2f}m/s)\n'.format(super().__str__(), self.speed(2096),
                                                              self.averageSpeed(2096))
        ret += '{} Cadence: {:.2f}rpm (avg: {:.2f}rpm)\n'.format(super().__str__(), self.cadence, self.averageCadence)
        ret += '{} Total Distance: {:.2f}m\n'.format(super().__str__(), self.totalDistance(2096))
        ret += '{} Total Revolutions: {:d}'.format(super().__str__(), self.totalRevolutions)
        return ret

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
            return 0
        elif self.cumulativeSpeedRevolutionCount < self.previous.cumulativeSpeedRevolutionCount:
            # Rollover
            return (
                       self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount) + self.maxSpeedRevCount
        else:
            return self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount

    @lazyproperty
    def cadenceRevCountDiff(self):
        if self.previous is None:
            return 0
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

    def distance(self, c):
        """
        :param c: circumference of the wheel (mm)
        :return: The distance since the last message (m)
        """
        return self.speedRevCountDiff * c / 1000

    def totalDistance(self, c):
        """
        :param c: circumference of the wheel (mm)
        :return: The total distance since the first message (m)
        """
        return self.totalSpeedRevolutions * c / 1000

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

    @lazyproperty
    def averageCadence(self):
        """
        Returns the average cadence since the first message
        :return: RPM
        """
        if self.firstTimestamp == self.timestamp:
            return self.cadence
        return self.totalRevolutions * 60 / (self.timestamp - self.firstTimestamp)

    def averageSpeed(self, c):
        """
        Returns the average speed since the first message
        :param c: circumference of the wheel (mm)
        :return: m/s
        """
        if self.firstTimestamp == self.timestamp:
            return self.speed(c)
        return self.totalDistance(c) / (self.timestamp - self.firstTimestamp)
