
__all__ = ['Atom', 'Binary', 'Tuple', 'Maps', 'ErlString',
           'Reference', 'Port', 'PID', 'Export']

class Atom(str):
    def __str__(self):
        return super(Atom, self).__str__()

    def __repr__(self):
        return "Atom(%s)" % super(Atom, self).__repr__()

class Binary(bytes):
    def __str__(self):
        b = self.hex()
        num_list = [str(int(b, 16)) for b in [b[i:i+2] for i in range(0, len(b), 2)]]
        return "<<"+",".join(num_list)+">>"

class Tuple(tuple):
    def __str__(self) -> str:
        return "{%s}"%(",".join([str(i) for i in self]),)

class Maps(dict):
    def __str__(self) -> str:
        return "#{%s}"%(",".join(["%s => %s"%(k,v) for k,v in self.items()]),)

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

