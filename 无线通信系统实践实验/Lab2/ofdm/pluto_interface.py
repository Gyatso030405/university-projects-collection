# -*- coding: utf-8 -*-
# @Author  : Zhirong Tang
# @Time    : 2021/12/20 12:58 PM

from optparse import OptionParser
import sys
import adi


class pluto_interface(object):
    def __init__(self, istx, args, freq=None, bandwidth=None, gain=None):
        # FIXME: format of ip args
        self.pluto = adi.Pluto(args)
        self._istx = istx
        self._args = args
        self._freq = self.set_freq(freq)
        self._rate = self.set_sample_rate(bandwidth)
        self._gain = self.set_gain(gain)

    def set_freq(self, freq=None):
        if freq is None:
            sys.stderr.write("\nYou must specify frequency.\n")
            sys.exit(1)
        try:
            if self._istx:
                self.pluto.tx_lo = int(freq)
            else:
                self.pluto.rx_lo = int(freq)
            return freq
        except Exception:
            sys.stderr.write(("\nRequested frequency (%f) out of range!\n" % freq))
            sys.exit(1)

    def set_sample_rate(self, bandwidth=None):
        if bandwidth is None:
            sys.stderr.write("\nYou must specify bandwidth.\n")
            sys.exit(1)
        try:
            self.pluto.sample_rate = int(bandwidth)
            return bandwidth
        except Exception:
            sys.stderr.write(("\nRequested bandwidth (%f) out of range!\n" % bandwidth))
            sys.exit(1)

    def set_gain(self, gain=None):
        if self._istx:
            if gain is None:
                self.pluto.tx_hardwaregain_chan0 = -5
                print("Setting Tx gain to -5dB (from [-90, 0]dB)")
            else:
                self.pluto.tx_hardwaregain_chan0 = gain
            return self.pluto.tx_hardwaregain_chan0
        else:
            if gain is None:
                self.pluto.rx_hardwaregain_chan0 = 0
                print("Setting Rx gain to 0dB (from [0, 75]dB)")
            else:
                self.pluto.rx_hardwaregain_chan0 = gain
            return self.pluto.rx_hardwaregain_chan0


    def _print_interface_verbage(self):
        """
        Prints information about the Pluto device
        """
        print("Args:      {}".format(self._args))
        print("Freq:      {}MHz".format(self._freq / 1e6))
        print("Bandwidth: {}MHz".format(self._rate / 1e6))
        print("Gain:      {}dB".format(self._gain))

# -------------------------------------------------------------------#
#   TRANSMITTER
# -------------------------------------------------------------------#
class pluto_transmitter(pluto_interface):
    def __init__(self, args, freq=None, bandwidth=None, gain=None, verbose=False):
        pluto_interface.__init__(self, True, args, freq, bandwidth, gain)
        if verbose:
            self._print_verbage()

    def add_options(parser):
        parser.add_option("", "--tx-args", type="string", default="ip:192.168.2.1",
                          help="PlutoSDR device address [default=%default]")
        parser.add_option("", "--tx-freq", type="float", default=915e6,
                          help="Set transmit frequency [default=%default]")
        parser.add_option("-W", "--bandwidth", type="float", default=1e6,
                          help="Set symbol bandwidth [default=%default]")
        parser.add_option("", "--tx-gain", type="float", default=-5,
                          help="Set transmit gain in dB [default=%default]")
        if not parser.has_option("--verbose"):
            parser.add_option("-v", "--verbose", action="store_true", default=False)

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the Pluto transmitter
        """
        print("\nPlutoSDR Transmitter:")
        self._print_interface_verbage()

#--------------------------------------------------------------------#
#   RECEIVER
#--------------------------------------------------------------------#
class pluto_receiver(pluto_interface):
    def __init__(self, args, freq=None, bandwidth=None, gain=None, buff=None, mode=None, verbose=False):
        pluto_interface.__init__(self, False, args, freq, bandwidth, gain)
        self._buff = self.set_rx_buffer(buff)
        self._mode = self.set_gain_control_mode(gain, mode)
        if verbose:
            self._print_verbage()

    def set_rx_buffer(self, buffer=None):
        if buffer is None:
            self.pluto.rx_buffer_size = 10000
            print("Setting Rx buffer size to 10000.")
            return buffer
        try:
            self.pluto.rx_buffer_size = int(buffer)
            return buffer
        except Exception:
            sys.stderr.write(("\nRequested rx buffer size (%f) out of range!\n" % buffer))
            sys.exit(1)

    def set_gain_control_mode(self, gain, mode=None):
        if mode is None or mode == "manual":
            self.pluto.gain_control_mode_chan0 = "manual"
            self._gain = self.set_gain(gain)
            return "manual"
        else:
            try:
                self.pluto.gain_control_mode_chan0 = mode
                self._gain = self.set_gain(gain)
                return mode
            except Exception:
                sys.stderr.write(("\nInvalid gain control mode!\n"))
                sys.exit(1)

    def add_options(parser):
        parser.add_option("", "--rx-args", type="string", default="ip:192.168.2.1",
                          help="PlutoSDR device address [default=%default]")
        parser.add_option("", "--rx-freq", type="float", default=915e6,
                          help="Set receive frequency [default=%default]")
        parser.add_option("-W", "--bandwidth", type="float", default=1e6,
                          help="Set symbol bandwidth [default=%default]")
        parser.add_option("", "--rx-gain", type="float", default=-5,
                          help="Set receive gain in dB [default=%default]")
        parser.add_option("", "--rx-buff", type="float", default=10000,
                          help="Set receive buffer [default=%default]")
        parser.add_option("", "--gain-mode", type="string", default="fast_attack",
                          help="Set AGC mode [default=%default]")
        if not parser.has_option("--verbose"):
            parser.add_option("-v", "--verbose", action="store_true", default=False)

    # Make a static method to call before instantiation
    add_options = staticmethod(add_options)

    def _print_verbage(self):
        """
        Prints information about the Pluto receiver
        """
        print("\nPlutoSDR Receiver:")
        self._print_interface_verbage()
        print("BufferSize:{}".format(int(self._buff)))
        print("GainMode:  {}".format(self._mode))
