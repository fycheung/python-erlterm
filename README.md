# Erlterm #

## Usage ##

此库可以实现把erlang数据序列化后的binary（erlang:term_to_binary()）转换成python的可识别的结构，或者把python数据序列化成erlang的binary格式，erlang可以通过binary_to_term反序列数据。
兼容otp22的类型定义，序列化atom类型时候python统一使用utf8形式。
另外也新增了codec.ErlangStrDecoder类，用于使用python直接解析文本形式的erlang结构。


[erlang binary term](http://erlang.org/doc/apps/erts/erl_ext_dist.html).

Basic usage is :

    need python3.x 
    
    import erlterm
    py_struct = erlterm.decode(binary_term)
    py_struct = decode_from_str(str(py_struct))
    binary = erlterm.encode(py_struct)


example:
```
    binary: [131,116,0,0,0,5,100,0,1,97,100,0,1,97,100,0,1,100,107,0,
            4,1,2,3,4,104,2,100,0,1,99,100,0,1,99,104,3,100,0,1,99,
            100,0,1,99,100,0,1,99,107,0,1,98,107,0,3,98,98,98,109,0,
            0,0,3,97,98,99,109,0,0,0,3,97,98,99]
    
    python_print_format:
            #{a => a,d => [1, 2, 3, 4],{c,c} => {c,c,c},"b" => "bbb",<<97,98,99>> => <<97,98,99>>}
    
    erl_format:
            #{a => a,
            d => [1,2,3,4],
            {c,c} => {c,c,c},
            "b" => "bbb",<<"abc">> => <<"abc">>}
```

types:

    自定义类型在erlterm.types.py, 主要增加了一些特殊兼容的类型，例如ErlString, 在erlang中没有字符串类型，
    此处使用了个兼容类型区分(erlang中由可见字符组成的列表对应python中的ErlString),
    然后大部分类型在pyhton类型基础上重写了__str__方法，方便打印出和erlang中一样的格式。
    
    | erlang type | python new type | python native type|
    |-------------|-----------------|-------------------|
    | atom        | Atom            | str               |
    | binary      | Binary          | bytes             |
    | tuple       | Tuple           | tuple             |
    | bitstring   | ErlString       | str               |
    | maps        | Maps            | dict              |
    | list        | List            | list              |
    | reference   | Reference       | Object            |
    | port        | Port            | Object            |
    | pid         | Pid             | Object            |
    | export      | Export          | Object            |
