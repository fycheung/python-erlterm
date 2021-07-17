
__all__ = ['Atom', 'Binary', 'Tuple', 'Maps', 'ErlString',
           'Reference', 'Port', 'PID', 'Export', 'List']



class Atom(str):
    def __str__(self):
        return super(Atom, self).__str__()

    def is_simple_atom(self):
        if not (self[0] >= 'a' and self[0] <= 'z'):
            return False

        for c in self:
            if (c >= 'a' and c <= 'z') or \
              (c >= 'A' and c <= 'Z') or \
              (c >= '0' and c <= '9') or \
              c == '_' or c == '@':
                continue
            else:
                return False
        return True

    def __repr__(self):
        if self.is_simple_atom():
            return "Atom(%s)" % super(Atom, self).__repr__()
        else:
            return "Atom(%s)" % super(Atom, self).__repr__()

    def __str__(self):
        if self.is_simple_atom():
            return super(Atom, self).__str__()
        else:
            return "'%s'"%  super(Atom, self).__str__()

class Binary(bytes):
    def is_visible(self):
        for c in self:
            if c < 32 or c > 126:
                return False
        return True

    def __str__(self):
        # b = self.hex()
        # num_list = [str(int(b, 16)) for b in [b[i:i+2] for i in range(0, len(b), 2)]]
        if self.is_visible():
            return "<<\"%s\">>"% super(Binary, self).__str__()[2:-1]
        else:
            return "<<%s>>"%(",".join([str(c) for c in self]), )

class Tuple(tuple):
    def __str__(self) -> str:
        return "{%s}"%(",".join([str(i) for i in self]),)

class Maps(dict):
    def __str__(self) -> str:
        return "#{%s}"%(",".join(["%s => %s"%(k,v) for k,v in self.items()]),)

class List(list):
    def __str__(self) -> str:
        return "[%s]"%(",".join([str(item) for item in self]),)

# visible simple string
class ErlString(str):
    def __init__(self, string) -> None:
        if len(string) > 65535:
            raise ValueError("string len over 65535")
        for i in self:
            if ord(i) > 126 or ord(i) < 32:
                raise ValueError("string char must in range 32-126")
        super(ErlString, self).__init__()

    def __str__(self) -> str:       
        return '"%s"'%(super(ErlString,self).__str__(),)

class Reference(object):
    def __init__(self, node, ref_id, creation):
        if not isinstance(ref_id, tuple):
            ref_id = tuple(ref_id)
        self.node = node
        self.ref_id = ref_id
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, Reference) and self.node == other.node and self.ref_id == other.ref_id and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Ref<%d.%s>" % (self.creation, ".".join(str(i) for i in self.ref_id))

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class Port(object):
    def __init__(self, node, port_id, creation):
        self.node = node
        self.port_id = port_id
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, Port) and self.node == other.node and self.port_id == other.port_id and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Port<%d.%d>" % (self.creation, self.port_id)

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class PID(object):
    def __init__(self, node, pid_id, serial, creation):
        self.node = node
        self.pid_id = pid_id
        self.serial = serial
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, PID) and self.node == other.node and self.pid_id == other.pid_id and self.serial == other.serial and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<%d.%d.%d>" % (self.creation, self.pid_id, self.serial)

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class Export(object):
    def __init__(self, module, function, arity):
        self.module = module
        self.function = function
        self.arity = arity

    def __eq__(self, other):
        return isinstance(other, Export) and self.module == other.module and self.function == other.function and self.arity == other.arity
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Fun<%s.%s.%d>" % (self.module, self.function, self.arity)

    def __repr__(self):
        return self.__str__()

