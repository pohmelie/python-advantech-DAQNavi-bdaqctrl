from cffi import FFI


ffi = FFI()
with open("_bdaqctrl.h") as fin:

    ffi.cdef(fin.read())

bdaqctrl = ffi.dlopen("libbiodaq.so")


class Dio:

    def __init__(self, dev_info="PCI-1756, BID#0"):

        self.info = ffi.new("DeviceInformation *")
        self.info.Description = dev_info
        self.info.DeviceNumber = -1
        self.info.DeviceMode = bdaqctrl.ModeWriteWithReset
        self.info.ModuleIndex = 0

        self.di = bdaqctrl.AdxInstantDiCtrlCreate()
        self.do = bdaqctrl.AdxInstantDoCtrlCreate()

        assert bdaqctrl.Success == bdaqctrl.InstantDiCtrl_setSelectedDevice(
            self.di, self.info)
        assert bdaqctrl.Success == bdaqctrl.InstantDoCtrl_setSelectedDevice(
            self.do, self.info)

        self.di_port_count = bdaqctrl.InstantDiCtrl_getPortCount(self.di)
        self.do_port_count = bdaqctrl.InstantDoCtrl_getPortCount(self.do)

        count = max(self.di_port_count, self.do_port_count)
        self.buffer = ffi.new("unsigned char []", count)

    def in_read_all(self):

        assert bdaqctrl.Success == bdaqctrl.InstantDiCtrl_ReadAny(
            self.di,
            0,
            self.di_port_count,
            self.buffer,
        )
        return list(self.buffer)

    def out_read_all(self):

        assert bdaqctrl.Success == bdaqctrl.InstantDoCtrl_ReadAny(
            self.do,
            0,
            self.do_port_count,
            self.buffer,
        )
        return list(self.buffer)

    def _parse_address(self, address):

        return address if isinstance(address, tuple) else divmod(address, 8)

    def in_read_bit(self, address):

        port, bit = self._parse_address(address)
        data = self.in_read_all()
        return (data[port] >> bit) & 1

    def out_read_bit(self, address):

        port, bit = self._parse_address(address)
        data = self.out_read_all()
        return (data[port] >> bit) & 1

    def out_write_all(self, data):

        for i, v in enumerate(data):

            self.buffer[i] = v

        count = min(self.do_port_count, len(data))
        assert bdaqctrl.Success == bdaqctrl.InstantDoCtrl_WriteAny(
            self.do,
            0,
            count,
            self.buffer,
        )

    def out_write_bit(self, address, value):

        port, bit = self._parse_address(address)
        data = self.out_read_all()
        if value:

            data[port] = data[port] | (1 << bit)

        else:

            data[port] = data[port] & ~(1 << bit)

        self.out_write_all(data)


class Ai:

    def __init__(self, dev_info="PCI-1713U, BID#0"):

        self.info = ffi.new("DeviceInformation *")
        self.info.Description = dev_info
        self.info.DeviceNumber = -1
        self.info.DeviceMode = bdaqctrl.ModeWriteWithReset
        self.info.ModuleIndex = 0

        self.ai = bdaqctrl.AdxInstantAiCtrlCreate()
        assert bdaqctrl.Success == bdaqctrl.InstantAiCtrl_setSelectedDevice(
            self.ai, self.info)

        self.channels = bdaqctrl.InstantAiCtrl_getChannels(self.ai)
        self.buffer = ffi.new("double []", self.channel_count)

    @property
    def channel_count(self):

        return bdaqctrl.InstantAiCtrl_getChannelCount(self.ai)

    def set_range(self, channel_id, mode):

        channel = bdaqctrl.ICollection_getItem(self.channels, channel_id)
        assert bdaqctrl.Success == bdaqctrl.AnalogInputChannel_setValueRange(
            channel, mode)

    def set_type(self, channel_id, mode):

        channel = bdaqctrl.ICollection_getItem(self.channels, channel_id)
        assert bdaqctrl.Success == bdaqctrl.AnalogInputChannel_setSignalType(
            channel, mode)

    def read_all(self):

        assert bdaqctrl.Success == bdaqctrl.InstantAiCtrl_ReadAny(
            self.ai,
            0,
            self.channel_count,
            ffi.NULL,
            self.buffer
        )
        return tuple(map(self.buffer.__getitem__, range(self.channel_count)))

    def read(self, channel_id):

        return self.read_all()[channel_id]


class Ao:

    def __init__(self, dev_info="PCI-1720, BID#0"):

        self.info = ffi.new("DeviceInformation *")
        self.info.Description = dev_info
        self.info.DeviceNumber = -1
        self.info.DeviceMode = bdaqctrl.ModeWriteWithReset
        self.info.ModuleIndex = 0

        self.ao = bdaqctrl.AdxInstantAoCtrlCreate()
        assert bdaqctrl.Success == bdaqctrl.InstantAoCtrl_setSelectedDevice(
            self.ao, self.info)

        self.channels = bdaqctrl.InstantAoCtrl_getChannels(self.ao)

    @property
    def channel_count(self):

        return bdaqctrl.InstantAoCtrl_getChannelCount(self.ao)

    def set_range(self, channel_id, mode):

        channel = bdaqctrl.ICollection_getItem(self.channels, channel_id)
        assert bdaqctrl.Success == bdaqctrl.AnalogChannel_setValueRange(
            channel, mode)

    def write(self, channel_id, value):  # value from 0.0 to 1.0 inclusive

        assert bdaqctrl.Success == bdaqctrl.InstantAoCtrl_WriteAny(
            self.ao,
            channel_id,
            1,
            ffi.NULL,
            ffi.new("double *", value),
        )


if __name__ == "__main__":

    import time

    print("================= dio")
    dio = Dio()
    print(dio.in_read_all())
    print(dio.in_read_bit((1, 3)))
    print(dio.in_read_bit(11))
    print("out")
    dio.out_write_all([1, 2, 3, 4])
    print(dio.out_read_all())
    print(dio.out_read_bit(11))
    dio.out_write_bit(11, 1)
    print(dio.out_read_bit(11))

    print("================= ai")
    ai = Ai()
    print(ai.channel_count)
    for i in range(ai.channel_count):

        ai.set_type(i, bdaqctrl.Differential)
        ai.set_range(i, bdaqctrl.V_0To10)

    print(ai.channel_count)
    for _ in range(3):

        print(ai.read_all())
        time.sleep(0.1)

    print("================= ao")
    ao = Ao()
    print(ao.channel_count)
    ao.set_range(0, bdaqctrl.V_0To10)
    ao.write(0, 0.5)
