# Erlastic #

## Usage ##

此库可以实现把erlang数据序列化后的binary（erlang:term_to_binary()）转换成python的可识别的结构，或者把python数据序列化成erlang的binary格式，erlang可以通过binary_to_term反序列数据。
兼容otp22的类型定义，序列化atom类型时候python统一使用utf8形式。

[erlang binary term](http://erlang.org/doc/apps/erts/erl_ext_dist.html).

Basic usage is :

    need python3.x 
    
    import erlastic
    py_struct = erlastic.decode(binary_term)
    binary = erlastic.encode(py_struct)


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


自定义的python兼容类型：
    自定义类型在erlastic.types.py, 主要增加了一些特殊兼容的类型，例如ErlString, 在erlang中没有字符串类型，
    此处使用了个兼容类型区分，然后大部分类型在pyhton类型基础上重写了__str__方法，方便打印出和erlang中一样的格式。
