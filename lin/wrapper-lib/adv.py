import bdaqctrl


def check(expect, f, *args, **kwargs):

    bound = lambda x: x if x >=0 else 2 ** 32 + x
    r = f(*args, **kwargs)
    if r != expect:

        raise Exception(
            str.format(
                "Function '{}' returns '0x{:x}', expected '0x{:x}'",
                f.__name__,
                bound(r),
                bound(expect)
            )
        )


class Dio:

    def __init__(self, dev_info="PCI-1756, BID#0"):

        self.info = bdaqctrl.DeviceInformation(dev_info)
        self.di = bdaqctrl.AdxInstantDiCtrlCreate()
        self.do = bdaqctrl.AdxInstantDoCtrlCreate()

        for d in (self.di, self.do):

            check(bdaqctrl.Success, d.setSelectedDevice, self.info)

        self.di_port_count = self.di.getPortCount()
        self.do_port_count = self.do.getPortCount()
        self.b = bdaqctrl.UCharArray(max(self.di_port_count, self.do_port_count))


    def cleanup(self):

        self.di.Cleanup()
        self.do.Cleanup()


    def _read_all(self, d, pc):

        check(bdaqctrl.Success, d.Read, 0, pc, self.b)
        data = list(map(lambda i: self.b[i], range(pc)))
        return data


    def in_read_all(self):

        return self._read_all(self.di, self.di_port_count)


    def out_read_all(self):

        return self._read_all(self.do, self.do_port_count)


    def _parse_address(self, address):

        return address if isinstance(address, tuple) else divmod(address, 8)


    def _read_bit(self, reader, address):

        address, channel = self._parse_address(address)
        data = reader()
        bit = (data[address] >> channel) & 1
        return bit


    def in_read_bit(self, address):

        return self._read_bit(self.in_read_all, address)


    def out_read_bit(self, address):

        return self._read_bit(self.out_read_all, address)


    def out_write_all(self, data):

        for i, v in enumerate(data):

            self.b[i] = v

        check(bdaqctrl.Success, self.do.Write, 0, min(self.do_port_count, len(data)), self.b)


    def out_write_bit(self, address, value):

        address, channel = self._parse_address(address)
        data = self.out_read_all()
        if value:

            data[address] = data[address] | (1 << channel)

        else:

            data[address] = data[address] & ~(1 << channel)

        self.out_write_all(data)


class Ai:

    def __init__(self, dev_info="PCI-1713U, BID#0"):

        self.info = bdaqctrl.DeviceInformation(dev_info)
        self.ai = bdaqctrl.AdxInstantAiCtrlCreate()
        check(bdaqctrl.Success, self.ai.setSelectedDevice, self.info)

        self.channels = self.ai.getChannels()
        self.buf = bdaqctrl.DoubleArray(32)


    def set_range(self, channel, mode):

        self.channels.getItem(channel).setValueRange(mode)


    def read_all(self):

        self.ai.Read(0, 32, self.buf)
        return tuple(map(lambda i: self.buf[i], range(32)))


    def read(self, channel):

        return self.read_all()[channel]


class Ao:

    def __init__(self, dev_info="PCI-1720, BID#0"):

        self.info = bdaqctrl.DeviceInformation(dev_info)
        self.ao = bdaqctrl.AdxInstantAoCtrlCreate()
        check(bdaqctrl.Success, self.ao.setSelectedDevice, self.info)

        self.channels = self.ao.getChannels()


    def set_range(self, channel, mode):

        check(0, self.channels.getItem(channel).setValueRange, mode)


    def write(self, ch, value):  # value from 0.0 to 1.0 inclusive

        self.ao.Write(ch, max(0, min(int(value * (1 << 12)), 0xfff)))
