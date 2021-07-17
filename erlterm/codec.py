
from __future__ import division

import struct
import zlib

from erlterm.constants import *
from erlterm.types import *

__all__ = ["ErlangTermEncoder", "ErlangTermDecoder", "ErlangStrDecoder", "EncodingError"]

class EncodingError(Exception):
    pass

class ErlangTermDecoder(object):
    def __init__(self):
        # Cache decode functions to avoid having to do a getattr
        self.decoders = {}
        for k in self.__class__.__dict__:
            v = getattr(self, k)
            if callable(v) and k.startswith('decode_'):
                try: self.decoders[int(k.split('_')[1])] = v
                except: pass

    def decode(self, buf, offset=0):
        version = buf[offset]
        if version != FORMAT_VERSION:
            raise EncodingError("Bad version number. Expected %d found %d" % (FORMAT_VERSION, version))
        return self.decode_part(buf, offset+1)[0]

    def decode_part(self, buf, offset=0):
        return self.decoders[buf[offset]](buf, offset+1)

    def decode_97(self, buf, offset):
        """SMALL_INTEGER_EXT"""
        return buf[offset], offset+1

    def decode_98(self, buf, offset):
        """INTEGER_EXT"""
        return struct.unpack(">l", buf[offset:offset+4])[0], offset+4

    def decode_99(self, buf, offset):
        """FLOAT_EXT"""
        return float(buf[offset:offset+31].split(b'\x00', 1)[0]), offset+31

    def decode_70(self, buf, offset):
        """NEW_FLOAT_EXT"""
        return struct.unpack(">d", buf[offset:offset+8])[0], offset+8

    def decode_100(self, buf, offset):
        """ATOM_EXT"""
        atom_len = struct.unpack(">H", buf[offset:offset+2])[0]
        atom = buf[offset+2:offset+2+atom_len]
        return self.convert_atom(atom), offset+atom_len+2

    def decode_115(self, buf, offset):
        """SMALL_ATOM_EXT"""
        atom_len = buf[offset]
        atom = buf[offset+1:offset+1+atom_len]
        return self.convert_atom(atom), offset+atom_len+1

    def decode_118(self, buf, offset):
        """ATOM_UTF8_EXT"""
        atom_len = struct.unpack(">H", buf[offset:offset+2])[0]
        atom = buf[offset+2:offset+2+atom_len]
        return self.convert_atom(atom, "utf-8"), offset+atom_len+2


    def decode_119(self, buf, offset):
        """SMALL_ATOM_UTF8_EXT"""
        atom_len = buf[offset]
        atom = buf[offset+1:offset+1+atom_len]
        return self.convert_atom(atom, "utf-8"), offset+atom_len+1

    def decode_104(self, buf, offset):
        """SMALL_TUPLE_EXT"""
        arity = buf[offset]
        offset += 1

        items = []
        for i in range(arity):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        return Tuple(items), offset

    def decode_105(self, buf, offset):
        """LARGE_TUPLE_EXT"""
        arity = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4

        items = []
        for i in range(arity):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        return Tuple(items), offset

    def decode_106(self, buf, offset):
        """NIL_EXT"""
        return [], offset

    def decode_107(self, buf, offset):
        """STRING_EXT"""
        length = struct.unpack(">H", buf[offset:offset+2])[0]
        st = buf[offset+2:offset+2+length]

        st_list = []
        is_string = True
        for c in st:
            c_int = c if isinstance(c, int) else ord(c)
            st_list.append(c_int)
            if c_int < 32 or c_int >126:
                is_string = False

        re = ErlString(st.decode("ascii")) if is_string else st_list
        return re, offset+2+length

    def decode_108(self, buf, offset):
        """LIST_EXT"""
        length = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4
        items = []
        for i in range(length):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        tail, offset = self.decode_part(buf, offset)
        if tail != []:
            # TODO: Not sure what to do with the tail
            raise NotImplementedError("Lists with non empty tails are not supported")
        return List(items), offset

    def decode_109(self, buf, offset):
        """BINARY_EXT"""
        length = struct.unpack(">L", buf[offset:offset+4])[0]
        return Binary(buf[offset+4:offset+4+length]), offset+4+length

    def decode_110(self, buf, offset):
        """SMALL_BIG_EXT"""
        n = buf[offset]
        offset += 1
        return self.decode_bigint(n, buf, offset)

    def decode_111(self, buf, offset):
        """LARGE_BIG_EXT"""
        n = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4
        return self.decode_bigint(n, buf, offset)

    def decode_bigint(self, n, buf, offset):
        sign = buf[offset]
        offset += 1
        b = 1
        val = 0
        for i in range(n):
            val += buf[offset] * b
            b <<= 8
            offset += 1
        if sign != 0:
            val = -val
        return val, offset

    def decode_101(self, buf, offset):
        """REFERENCE_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing REFERENCE_EXT, found %r instead" % node)
        reference_id, creation = struct.unpack(">LB", buf[offset:offset+5])
        return Reference(node, [reference_id], creation), offset+5

    def decode_114(self, buf, offset):
        """NEW_REFERENCE_EXT"""
        id_len = struct.unpack(">H", buf[offset:offset+2])[0]
        node, offset = self.decode_part(buf, offset+2)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing NEW_REFERENCE_EXT, found %r instead" % node)
        creation = buf[offset]
        reference_id = struct.unpack(">%dL" % id_len, buf[offset+1:offset+1+4*id_len])
        return Reference(node, reference_id, creation), offset+1+4*id_len

    def decode_102(self, buf, offset):
        """PORT_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PORT_EXT, found %r instead" % node)
        port_id, creation = struct.unpack(">LB", buf[offset:offset+5])
        return Port(node, port_id, creation), offset+5

    def decode_103(self, buf, offset):
        """PID_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PID_EXT, found %r instead" % node)
        pid_id, serial, creation = struct.unpack(">LLB", buf[offset:offset+9])
        return PID(node, pid_id, serial, creation), offset+9

    def decode_113(self, buf, offset):
        """EXPORT_EXT"""
        module, offset = self.decode_part(buf, offset)
        if not isinstance(module, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % module)
        function, offset = self.decode_part(buf, offset)
        if not isinstance(function, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % function)
        arity, offset = self.decode_part(buf, offset)
        if not isinstance(arity, int):
            raise EncodingError("Expected integer while parsing EXPORT_EXT, found %r instead" % arity)
        return Export(module, function, arity), offset+1

    def decode_116(self, buf, offset):
        """MAP_EXT"""
        arity = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4
        maps = {}
        for i in range(arity):
            key, offset = self.decode_part(buf, offset)
            value, offset = self.decode_part(buf, offset)
            maps[key] = value
        return Maps(maps), offset

    def decode_80(self, buf, offset):
        """Compressed term"""
        usize = struct.unpack(">L", buf[offset:offset+4])[0]
        buf = zlib.decompress(buf[offset+4:offset+4+usize])
        return self.decode_part(buf, 0)

    def convert_atom(self, atom, encoding='latin-1'):
        # if atom == b"true":
        #     return True
        # elif atom == b"false":
        #     return False
        # elif atom == b"none":
        #     return None
        return Atom(atom.decode(encoding))
    

def inspect_strip(func):
    def inspect_strip1(obj):
        obj.skip_space()
        rt = func(obj)
        obj.skip_space()
        return rt
    return inspect_strip1

def ascii_list_to_bytes(ascii_list):
    return "".join([chr(c) for c in ascii_list])

class ErlangStrDecoder(object):
    def parse(self, s):
        s = s.strip()

        if not s:
            return ""

        self.i = 0
        self.n = len(s)
        self.s = s

        return self.parse_value()
    
    @inspect_strip
    def parse_value(self):
        if self.c() == "[":
            self.i += 1
            return self.parse_list()

        elif self.c() == "{":
            self.i += 1
            return self.parse_tuple()

        elif self.c() == "#" and self.c(1) == "{" :
            self.i += 2
            return self.parse_map()

        elif self.c() == "<" and self.c(1) == "<" and self.c(2) == "\"":
            self.i += 3
            return self.parse_simple_binary()

        elif self.c() == "<" and self.c(1) == "<" :
            self.i += 2
            return self.parse_binary()

        elif self.c() == "\"":
            self.i += 1
            return self.parse_str()

        elif self.is_digit() or self.c() == "-":
            return self.parse_num()

        elif self.c() == "'":
            self.i += 1
            return self.parse_atom_with_single_quotes()

        elif self.c() >= 'a' and self.c() <= 'z':
            return self.parse_atom()

        else:
            raise NotImplementedError("not supported format at index:%s,char:%s"%(self.i, self.c()))

    def parse_list(self):
        rt = []
        while self.c() != "]":
            rt.append(self.parse_value())
            if self.c() == ",":
                self.i += 1
            
        self.i += 1
        return rt

    def parse_tuple(self):
        rt = []
        while self.c() != "}":
            rt.append(self.parse_value())
            if self.c() == ",":
                self.i += 1
        self.i += 1
        return Tuple(rt)

    def parse_binary(self):
        rt = []
        while self.c() != ">" and self.c(1) != ">":
            self.skip_space()
            rt.append(self.parse_num())
            self.skip_space()
            if self.c() == ",":
                self.i += 1
        self.i += 2
        return Binary(rt)

    def parse_simple_binary(self):
        Str = self.parse_str()
        if self.c() == ">" and self.c(1) == ">":
            self.i += 2
            return Binary(Str, "utf8")
        else:
            raise NotImplementedError("not supported binary end at:%s"%Str)


    def parse_str(self):
        start = self.i
        while self.c() != '"':
            if self.is_escape_char():
                self.i += 2
            else:
                self.i += 1
        self.i += 1
        return ErlString(self.s[start:self.i-1])


    def parse_num(self):
        is_negative = False
        is_float = False
        if self.c() == "-":
            is_negative = True
            self.i += 1
        start = self.i
        while self.i < self.n and (self.is_digit() or self.c() == '.'):
            if self.c() == '.':
                is_float = True
            self.i += 1

        if is_float:
            rt = float(self.s[start:self.i])
        else:
            rt = int(self.s[start:self.i])

        return -rt if is_negative else rt

    def parse_map(self):
        rt = {}
        while self.c() != "}":
            k = self.parse_value()
            if self.c() == "=" and self.c(1) == ">":
                self.i += 2
            rt[k] = self.parse_value()
            if self.c() == ",":
                self.i += 1

        return Maps(rt)

    def parse_atom(self):
        start = self.i
        while self.i < self.n and \
              ((self.c() >= 'a' and self.c() <= 'z') or \
               (self.c() >= 'A' and self.c() <= 'Z') or \
               self.is_digit() or \
               self.c() == '_' or self.c() == '@'):
            self.i += 1
        return Atom(self.s[start:self.i])

    def parse_atom_with_single_quotes(self):
        start = self.i
        while self.c() != "'":
            if self.is_escape_char():
                self.i += 2
            else:
                self.i += 1
        self.i += 1
        return Atom(self.s[start:self.i-1])

    def is_digit(self):
        return self.c() >= "0" and self.c() <= "9"

    def skip_space(self):
        while self.i < self.n and self.c().isspace():
            self.i += 1

    def c(self, offset=0):
        return self.s[self.i+offset]

    def is_escape_char(self):
        escape_char = ['"', '\'','\\', '/',
                        'b', 'f', 'n', 'r', 't']
        return self.c() == "\\" and self.c(1) in escape_char


class ErlangTermEncoder(object):
    def __init__(self, encoding="utf-8", unicode_type="binary"):
        self.encoding = encoding
        self.unicode_type = unicode_type

    def encode(self, obj, compressed=False):
        import sys
        import pprint
        #pprint.pprint(self.encode_part(obj),stream=sys.stderr)
        ubuf = b"".join(self.encode_part(obj))
        if compressed is True:
            compressed = 6
        if not (compressed is False \
                    or (isinstance(compressed, int) \
                            and compressed >= 0 and compressed <= 9)):
            raise TypeError("compressed must be True, False or "
                            "an integer between 0 and 9")
        if compressed:
            cbuf = zlib.compress(ubuf, compressed)
            if len(cbuf) < len(ubuf):
                usize = struct.pack(">L", len(ubuf))
                ubuf = "".join([COMPRESSED, usize, cbuf])
        return bytes([FORMAT_VERSION]) + ubuf

    def encode_part(self, obj):
        if obj is False:
            return [bytes([ATOM_EXT]), struct.pack(">H", 5), b"false"]
        elif obj is True:
            return [bytes([ATOM_EXT]), struct.pack(">H", 4), b"true"]
        elif obj is None:
            return [bytes([ATOM_EXT]), struct.pack(">H", 4), b"none"]
        elif isinstance(obj, int):
            if 0 <= obj <= 255:
                return [bytes([SMALL_INTEGER_EXT,obj])]
            elif -2147483648 <= obj <= 2147483647:
                return [bytes([INTEGER_EXT]), struct.pack(">l", obj)]
            else:
                sign = obj < 0
                obj = abs(obj)

                big_buf = []
                while obj > 0:
                    big_buf.append(obj & 0xff)
                    obj >>= 8

                if len(big_buf) < 256:
                    return [bytes([SMALL_BIG_EXT,len(big_buf),sign]),bytes(big_buf)]
                else:
                    return [bytes([LARGE_BIG_EXT]), struct.pack(">L", len(big_buf)), bytes([sign]), bytes(big_buf)]
        elif isinstance(obj, float):
            floatstr = ("%.20e" % obj).encode('ascii')
            return [bytes([FLOAT_EXT]), floatstr + b"\x00"*(31-len(floatstr))]
        # elif isinstance(obj, Atom):
        #     st = obj.encode('latin-1')
        #     return [bytes([ATOM_EXT]), struct.pack(">H", len(st)), st]
        elif isinstance(obj, Atom):
            st = obj.encode('utf-8')
            if len(st) <= 256:
                return [bytes([SMALL_ATOM_UTF8_EXT]), bytes([len(st)]), st]
            else:
                return [bytes([ATOM_UTF8_EXT]), struct.pack(">H", len(st)), st]

        elif isinstance(obj, ErlString):
            return [bytes([STRING_EXT]), struct.pack(">H", len(obj)), obj.encode("ascii")]

        elif isinstance(obj, str):
            st = obj.encode('utf8')
            return [bytes([BINARY_EXT]), struct.pack(">L", len(st)), st]

        elif isinstance(obj, bytes):
            return [bytes([BINARY_EXT]), struct.pack(">L", len(obj)), obj]
            
        elif isinstance(obj, tuple):
            n = len(obj)
            if n < 256:
                buf = [bytes([SMALL_TUPLE_EXT,n])]
            else:
                buf = [bytes([LARGE_TUPLE_EXT]), struct.pack(">L", n)]
            for item in obj:
                buf += self.encode_part(item)
            return buf
        elif isinstance(obj, dict):
            n = len(obj)
            buf = [bytes([MAP_EXT]), struct.pack(">L", n)]
            for k,v in obj.items():
                buf += self.encode_part(k)
                buf += self.encode_part(v)
            return buf
        elif obj == []:
            return [bytes([NIL_EXT])]
        elif isinstance(obj, list):
            if self.is_optimize_list(obj):
                return [bytes([STRING_EXT]), struct.pack(">H", len(obj)), bytes(obj)]
            else:
                buf = [bytes([LIST_EXT]), struct.pack(">L", len(obj))]
                for item in obj:
                    buf += self.encode_part(item)
                buf.append(bytes([NIL_EXT])) # list tail - no such thing in Python
                return buf
        elif isinstance(obj, Reference):
            return [bytes([NEW_REFERENCE_EXT]),
                struct.pack(">H", len(obj.ref_id)),
                bytes([ATOM_EXT]), struct.pack(">H", len(obj.node)), obj.node.encode('latin-1'),
                bytes([obj.creation]), struct.pack(">%dL" % len(obj.ref_id), *obj.ref_id)]
        elif isinstance(obj, Port):
            return [bytes([PORT_EXT]),
                bytes([ATOM_EXT]), struct.pack(">H", len(obj.node)), obj.node.encode('latin-1'),
                struct.pack(">LB", obj.port_id, obj.creation)]
        elif isinstance(obj, PID):
           return [bytes([PID_EXT]),
                bytes([ATOM_EXT]), struct.pack(">H", len(obj.node)), obj.node.encode('latin-1'),
                struct.pack(">LLB", obj.pid_id, obj.serial, obj.creation)]
        elif isinstance(obj, Export):
            return [bytes([EXPORT_EXT]),
                bytes([ATOM_EXT]), struct.pack(">H", len(obj.module)), obj.module.encode('latin-1'),
                bytes([ATOM_EXT]), struct.pack(">H", len(obj.function)), obj.function.encode('latin-1'),
                bytes([SMALL_INTEGER_EXT,obj.arity])]
        else:
            raise NotImplementedError("Unable to serialize %r" % obj)
    
    def is_optimize_list(self, obj):
        for i in obj:
            if not (isinstance(i, int) and i >= 0 and i <= 255):
                return False
        return True

