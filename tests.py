#!/usr/bin/env python

import unittest

from erlterm import decode, encode, decode_from_str
from erlterm.types import *

erlang_term_binaries = [
    # nil
    ([], list, b"\x83j"),
    # binary
    (Binary(b"foo"), Binary, b'\x83m\x00\x00\x00\x03foo'),
    # atom
    (Atom("foo"), Atom, b'\x83w\x03foo'),
    # small integer
    (123, int, b'\x83a{'),
    # integer
    (12345, int, b'\x83b\x00\x0009'),
    # bytes
    (b'foo', bytes, b'\x83m\x00\x00\x00\x03foo'),
    # float
    (1.2345, float, b'\x83c1.23449999999999993072e+00\x00\x00\x00\x00\x00'),
    # tuple
    ((Atom("foo"), Binary("test","utf8"), 123), tuple, b'\x83h\x03w\x03foom\x00\x00\x00\x04testa{'),
    # list
    ([1024, Binary("test","utf8"), 4.096], list, b'\x83l\x00\x00\x00\x03b\x00\x00\x04\x00m\x00\x00\x00\x04testc4.09600000000000008527e+00\x00\x00\x00\x00\x00j'),
    # small big
    (12345678901234567890, int, b'\x83n\x08\x00\xd2\n\x1f\xeb\x8c\xa9T\xab'),
    # large big
    (123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890,
     int, b'\x83o\x00\x00\x01D\x00\xd2\n?\xce\x96\xf1\xcf\xacK\xf1{\xefa\x11=$^\x93\xa9\x88\x17\xa0\xc2\x01\xa5%\xb7\xe3Q\x1b\x00\xeb\xe7\xe5\xd5Po\x98\xbd\x90\xf1\xc3\xddR\x83\xd1)\xfc&\xeaH\xc31w\xf1\x07\xf3\xf33\x8f\xb7\x96\x83\x05t\xeci\x9cY"\x98\x98i\xca\x11bY=\xcc\xa1\xb4R\x1bl\x01\x86\x18\xe9\xa23\xaa\x14\xef\x11[}O\x14RU\x18$\xfe\x7f\x96\x94\xcer?\xd7\x8b\x9a\xa7v\xbd\xbb+\x07X\x94x\x7fI\x024.\xa0\xcc\xde\xef:\xa7\x89~\xa4\xafb\xe4\xc1\x07\x1d\xf3cl|0\xc9P`\xbf\xab\x95z\xa2DQf\xf7\xca\xef\xb0\xc4=\x11\x06*:Y\xf58\xaf\x18\xa7\x81\x13\xdf\xbdTl4\xe0\x00\xee\x93\xd6\x83V\xc9<\xe7I\xdf\xa8.\xf5\xfc\xa4$R\x95\xef\xd1\xa7\xd2\x89\xceu!\xf8\x08\xb1Zv\xa6\xd9z\xdb0\x88\x10\xf3\x7f\xd3sc\x98[\x1a\xac6V\x1f\xad0)\xd0\x978\xd1\x02\xe6\xfbH\x149\xdc).\xb5\x92\xf6\x91A\x1b\xcd\xb8`B\xc6\x04\x83L\xc0\xb8\xafN+\x81\xed\xec?;\x1f\xab1\xc1^J\xffO\x1e\x01\x87H\x0f.ZD\x06\xf0\xbak\xaagVH]\x17\xe6I.B\x14a2\xc1;\xd1+\xea.\xe4\x92\x15\x93\xe9\'E\xd0(\xcd\x90\xfb\x10'),
    
    ({Atom('a'): Atom('a'), Atom('d'): [1,2,3,4], (Atom('c'), Atom('c')): (Atom('c'), Atom('c'), Atom('c')), ErlString('b'): ErlString('bbb'), Binary(b'abc'): Binary(b'abc')},
    dict,
    b'\x83t\x00\x00\x00\x05w\x01aw\x01aw\x01dk\x00\x04\x01\x02\x03\x04h\x02w\x01cw\x01ch\x03w\x01cw\x01cw\x01ck\x00\x01bk\x00\x03bbbm\x00\x00\x00\x03abcm\x00\x00\x00\x03abc'
    )
]

#
erlang_term_binaries2 = [
    # reference
    (Reference('nonode@nohost', [33, 0, 0], 0), Reference, b'\x83r\x00\x03d\x00\rnonode@nohost\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00'),
    # function export
    (Export('jobqueue', 'stats', 0), Export, b'\x83qd\x00\x08jobqueued\x00\x05statsa\x00'),
    # port
    (Port('nonode@nohost', 455, 0), Port, b'\x83fd\x00\rnonode@nohost\x00\x00\x01\xc7\x00'),
    # pid
    (PID('nonode@nohost', 31, 0, 0), PID, b'\x83gd\x00\rnonode@nohost\x00\x00\x00\x1f\x00\x00\x00\x00\x00')
    
]

# str only support ascii
erlang_decode_to_python = [
    (ErlString("foo"), ErlString, b'\x83k\x00\x03foo')
]

python_encode_to_erlang = [
    ([102, 111, 111], list, b'\x83k\x00\x03foo'),
    (ErlString("foo"), ErlString, b'\x83k\x00\x03foo')
]

class ErlangTestCase(unittest.TestCase):
    def testDecode(self):
        for python, expected_type, erlang  in erlang_term_binaries + erlang_decode_to_python:
            # print(python)
            decoded = decode(erlang)
            decodedFromStr = decode_from_str(str(decoded))
            self.assertEqual(python, decoded)
            self.assertTrue(isinstance(decoded, expected_type))
            self.assertEqual(python, decodedFromStr)
    
    def testDecode2(self):
        for python, expected_type, erlang  in erlang_term_binaries2:
            decoded = decode(erlang)
            self.assertEqual(python, decoded)
            self.assertTrue(isinstance(decoded, expected_type))

    def testEncode(self):
        for python, expected_type, erlang  in erlang_term_binaries + python_encode_to_erlang:
            encoded = encode(python)
            self.assertEqual(erlang, encoded)
    
    


if __name__ == '__main__':
    unittest.main()
