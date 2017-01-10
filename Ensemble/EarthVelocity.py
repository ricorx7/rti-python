import logging
from Ensemble.Ensemble import Ensemble

logger = logging.getLogger("Earth Velocity")
logger.setLevel(logging.DEBUG)
FORMAT = '[%(asctime)-15s][%(levelname)s][%(funcName)s] %(message)s'
logging.basicConfig(format=FORMAT)

class EarthVelocity:
    """
    Earth Velocity DataSet.
    [Bin x Beam] data.
    """

    def __init__(self, num_elements, element_multipiler):
        self.ds_type = 10
        self.num_elements = num_elements
        self.element_multipiler = element_multipiler
        self.image = 0
        self.name_len = 8
        self.Name = "E000003"
        self.Velocities = []
        # Create enough entries for all the (bins x beams)
        # Initialize with bad values
        for bins in range(num_elements):
            bins = []
            for beams in range(element_multipiler):
                bins.append([Ensemble().BadVelocity])

            self.Velocities.append(bins)

    def decode(self, data):
        """
        Take the data bytearray.  Decode the data to populate
        the velocities.
        :param data: Bytearray for the dataset.
        """
        packet_pointer = Ensemble.GetBaseDataSize(self.name_len)

        for bin in range(self.num_elements):
            for beam in range(self.element_multipiler):
                self.Velocities[bin][beam] = Ensemble.GetFloat(packet_pointer, Ensemble().BytesInFloat, data)
                packet_pointer += Ensemble().BytesInFloat

        logger.debug(self.Velocities)
