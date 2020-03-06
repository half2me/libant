from libAnt.core import lazyproperty
from libAnt.profiles.profile import ProfileMessage


class HeartRateProfileMessage(ProfileMessage):
    """ Message from Heart Rate Monitor """

    def __init__(self, msg, previous):
        super().__init__(msg, previous)

    def __str__(self):
        return f'{self.heartrate}'

    @lazyproperty
    def heartrate(self):
        """ 
            Instantaneous heart rate. This value is
            intended to be displayed by the display
            device without further interpretation.
            If Invalid set to 0x00 
        """
        return self.msg.content[7]