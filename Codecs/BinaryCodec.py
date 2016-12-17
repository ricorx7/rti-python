import struct

from Ensemble.Ensemble import Ensemble
from Ensemble.BeamVelocity import BeamVelocity
from Ensemble.InstrumentVelocity import InstrumentVelocity
from Ensemble.EarthVelocity import EarthVelocity
from Ensemble.Amplitude import Amplitude
from Ensemble.Correlation import Correlation
from Ensemble.GoodBeam import GoodBeam
from Ensemble.GoodEarth import GoodEarth

from PyCRC.CRCCCITT import CRCCCITT

class BinaryCodec():
    """
    Decode RoweTech ADCP Binary data.
    """

    def __init__(self):
        print("codec")
        self.buffer = bytearray()

    def add(self, data):

        # Add to buffer and Decode
        self.buffer.extend(data)

        self.findEnsemble()

    def findEnsemble(self):

        delimiter = b'\x80'*16 # look for first 16 bytes of header
        ensStart = self.buffer.find(delimiter)

        #print("EnsStart: ", ensStart)
        #print("Buffer Size: ", len(self.buffer))

        if ensStart >= 0 and len(self.buffer) > Ensemble().HeaderSize + ensStart:
            #Decode the Ensemble
            self.decodeEnsemble(ensStart)

    def decodeEnsemble(self, ensStart):

        # Check Ensemble number
        ensNum = struct.unpack("I", self.buffer[ensStart+16:ensStart+20])
        #print(ensNum[0])
        #ensNumInv = struct.unpack("I", self.buffer[ensStart+20:ensStart+24])
        #print(self.ones_complement(ensNumInv[0]))


        # Check ensemble size
        payloadSize = struct.unpack("I", self.buffer[ensStart+24:ensStart+28])
        #print(payloadSize[0])
        #payloadSizeInv = struct.unpack("I", self.buffer[ensStart+28:ensStart+32])
        #print(self.ones_complement(payloadSizeInv[0]))

        # Ensure the entire ensemble is in the buffer
        if len(self.buffer) >= ensStart + Ensemble().HeaderSize + payloadSize[0] + Ensemble().ChecksumSize:
            # Check checksum
            checksumLoc = ensStart + Ensemble().HeaderSize + payloadSize[0]
            checksum = struct.unpack("I", self.buffer[checksumLoc:checksumLoc + Ensemble().ChecksumSize])

            # Calculate Checksum
            # Use only the payload for the checksum
            ens = self.buffer[ensStart + Ensemble().HeaderSize:ensStart + Ensemble().HeaderSize + payloadSize[0]]
            calcChecksum = CRCCCITT().calculate(input_data=bytes(ens))
            #print("Calc Checksum: ", calcChecksum)
            #print("Checksum: ", checksum[0])
            #print("Checksum good: ", calcChecksum == checksum[0])

            if checksum[0] == calcChecksum:
                print(ensNum[0])
                # Decode data
                ensemble = self.decodeDataSets(self.buffer[ensStart:ensStart + Ensemble().HeaderSize + payloadSize[0]])

                # Stream data

            # Remove ensemble from buffer
            ensEnd = ensStart + Ensemble().HeaderSize + payloadSize[0] + Ensemble().ChecksumSize
            del self.buffer[0:ensEnd]

    def decodeDataSets(self, ens):
        """
        Decode the datasets in the ensemble.
        :param ens: Ensemble data.  Decode the dataset.
        :return: Return the decoded ensemble.
        """
        #print(ens)
        packetPointer = Ensemble().HeaderSize
        type = 0
        numElements = 0
        elementMultiplier = 0
        imag = 0
        nameLen = 0
        name = ""
        dataSetSize = 0

        # Create the ensemble
        ensemble = Ensemble()

        # Add the raw data to the ensemble
        ensemble.AddRawData(ens)

        # Decode the ensemble datasets
        for x in range(Ensemble().MaxNumDataSets):
            # Check if we are at the end of the payload
            if packetPointer >= len(ens):
                break;

            # Get the dataset info
            ds_type = Ensemble.GetInt32(packetPointer + (Ensemble.BytesInInt32 * 0), Ensemble().BytesInInt32, ens)
            num_elements = Ensemble.GetInt32(packetPointer + (Ensemble.BytesInInt32 * 1), Ensemble().BytesInInt32, ens)
            element_multiplier = Ensemble.GetInt32(packetPointer + (Ensemble.BytesInInt32 * 2), Ensemble().BytesInInt32, ens)
            image = Ensemble.GetInt32(packetPointer + (Ensemble.BytesInInt32 * 3), Ensemble().BytesInInt32, ens)
            name_len = Ensemble.GetInt32(packetPointer + (Ensemble.BytesInInt32 * 4), Ensemble().BytesInInt32, ens)
            name = str(ens[packetPointer+(Ensemble.BytesInInt32 * 5):packetPointer+(Ensemble.BytesInInt32 * 5)+8], 'UTF-8')

            # Calculate the dataset size
            data_set_size = Ensemble.GetDataSetSize(ds_type, name_len, num_elements, element_multiplier)

            # Beam Velocity
            if "E000001" in name:
                print(name)
                bv = BeamVelocity(num_elements, element_multiplier)
                bv.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddBeamVelocity(bv)

            # Instrument Velocity
            if "E000002" in name:
                print(name)
                iv = InstrumentVelocity(num_elements, element_multiplier)
                iv.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddInstrumentVelocity(iv)

            # Earth Velocity
            if "E000003" in name:
                print(name)
                ev = EarthVelocity(num_elements, element_multiplier)
                ev.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddEarthVelocity(ev)

            # Amplitude
            if "E000004" in name:
                print(name)
                amp = Amplitude(num_elements, element_multiplier)
                amp.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddAmplitude(amp)

            # Correlation
            if "E000005" in name:
                print(name)
                corr = Correlation(num_elements, element_multiplier)
                corr.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddCorrelation(corr)

            # Good Beam
            if "E000006" in name:
                print(name)
                gb = GoodBeam(num_elements, element_multiplier)
                gb.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddGoodBeam(gb)

            # Good Earth
            if "E000007" in name:
                print(name)
                ge = GoodEarth(num_elements, element_multiplier)
                ge.decode(ens[packetPointer:packetPointer+data_set_size])
                ensemble.AddGoodEarth(ge)


            # Move the next dataset
            packetPointer += data_set_size

        return ensemble


