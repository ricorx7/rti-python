from Ensemble.Ensemble import Ensemble
from log import logger


class GoodEarth:
    """
    Good Earth DataSet.
    Indicate if the beam data is good.
    [Bin x Beam] data.
    """

    def __init__(self, num_elements, element_multiplier):
        self.ds_type = 10
        self.num_elements = num_elements
        self.element_multiplier = element_multiplier
        self.image = 0
        self.name_len = 8
        self.Name = "E000007"
        self.GoodEarth = []
        # Create enough entries for all the (bins x beams)
        # Initialize with bad values
        for bins in range(num_elements):
            bins = []
            for beams in range(element_multiplier):
                bins.append([0])

            self.GoodEarth.append(bins)

    def decode(self, data):
        """
        Take the data bytearray.  Decode the data to populate
        the velocities.
        :param data: Bytearray for the dataset.
        """
        packet_pointer = Ensemble.GetBaseDataSize(self.name_len)

        for beam in range(self.element_multiplier):
            for bin_num in range(self.num_elements):
                self.GoodEarth[bin_num][beam] = Ensemble.GetInt32(packet_pointer, Ensemble().BytesInInt32, data)
                packet_pointer += Ensemble().BytesInInt32

        logger.debug(self.GoodEarth)

