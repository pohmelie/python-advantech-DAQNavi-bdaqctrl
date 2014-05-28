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


    def _read_bit(self, reader, address, channel=None):

        if channel is None:

            address, channel = divmod(address, 8)

        data = reader()
        bit = (data[address] >> channel) & 1
        return bit


    def in_read_bit(self, address, channel=None):

        return self._read_bit(self.in_read_all, address, channel)


    def out_read_bit(self, address, channel=None):

        return self._read_bit(self.out_read_all, address, channel)


    def out_write_all(self, data):

        for i, v in enumerate(data):

            self.b[i] = v

        check(bdaqctrl.Success, self.do.Write, 0, min(self.do_port_count, len(data)), self.b)


    def out_write_bit(self, value, address, channel=None):

        if channel is None:

            address, channel = divmod(address, 8)

        data = self.out_read_all()
        if value:

            data[address] = data[address] | (1 << channel)

        else:

            data[address] = data[address] & ~(1 << channel)

        self.out_write_all(data)


if __name__ == "__main__":

    d = Dio()
    print(d.in_read_all())
    print(d.out_read_all())
    d.out_write_bit(1, 8)
    print(d.out_read_all())
    print(d.out_read_bit(8))
    d.out_write_bit(0, 8)
    print(d.out_read_all())
    d.cleanup()
