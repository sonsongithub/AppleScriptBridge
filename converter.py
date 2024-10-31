"""
This script creates Swift interface from Objective-C header file.
The header file is created by `sdef`.
"""
import re
import argparse

class Enum:
    """
    to be written
    """
    @classmethod
    def create(cls, string):
        enum_pattern = re.compile(r'(^enum (.+?) \{(.+?)\};)', re.DOTALL | re.MULTILINE)
        matched = enum_pattern.match(string)
        if matched is not None:
            name = matched.group(2)
            text = matched.group(3)
            define_pattern = re.compile(r'(\w+)\s*=\s*(.+?)[\s,$]', re.DOTALL | re.MULTILINE)
            defines = define_pattern.findall(text)
            if defines is not None:
                a = list(map(lambda x: EnumElement(enum_name=name, name=x[0], value=x[1]), defines))
                return Enum(name, a)
            else:
                raise ValueError('not matched')
        else:
            raise ValueError('not matched')

    def __init__(self, name, items):
        self.name = name
        self.items = items

    def dump(self):
        print('enum: ' + self.name)
        for item in self.items:
            print('  name: ' + item.name)
            print('  value: ' + item.value)
            print('  code: ' + item.code)

    def write(self):
        template = f"""@objc public enum {self.name} : AEKeyword {{\n"""
        template += '\n'.join(map(lambda x: f'    case {x.name} = {x.code}', self.items))
        template += '\n};\n'
        return template

class EnumElement:
    """
    to be written
    """
    def __init__(self, enum_name, name, value):
        remove_pre = name.replace(enum_name, '')
        self.name = remove_pre[0].lower() + remove_pre[1:]
        self.value = value
        pattern = re.compile(r"'(.+?)'", re.DOTALL)
        matched = pattern.search(value)
        if matched is not None:
            self.value = matched.group(1)
            self.type = 'char'
            self.code = '0x' + ''.join(map(lambda c: f'{ord(c):02x}', self.value))
        else:
            self.value = value
            self.type = 'unknown'
            self.code = ''

class Argument:
    def __init__(self, label, type_, name):
        self.label = label
        self.type = type_
        self.original_type = type_
        self.name = name

class Function:
    """
    to be written
    """
    @classmethod
    def create(cls, string):
        function_pattern = re.compile(r'- \((.+?)\) (\w+?);', re.DOTALL)

        # pattern 1
        r = function_pattern.match(string)
        if r is not None:
            return Function(return_type=r.group(1), arguments=[Argument(label=r.group(2), type_=None, name=None)])

        # pattern 2
        function_pattern = re.compile(r'- \((.+?)\) ', re.DOTALL)
        r = function_pattern.match(string)
        if r is None:
            raise ValueError('not matched')

        return_type = r.group(1)
        arg_pattern = re.compile(r'([\w|\d]+)\:\((.+?)\)([\w|\d]+?)[\s|;]', re.DOTALL)
        args = arg_pattern.findall(string)
        arg_infos = []
        for arg in args:
            arg_infos.append(Argument(label=arg[0], type_=arg[1], name=arg[2]))

        return Function(return_type=return_type, arguments=arg_infos)


    def __init__(self, return_type, arguments):
        self.return_type = return_type
        self.arguments = arguments

    def write(self):
        buffer = self.arguments.copy()

        arg = buffer.pop(0)

        argument_string = []

        name = f'    @objc optional func {arg.label}'
        # name
        if arg.type is not None:
            argument_string.append(f'{arg.name}: {arg.type}')

        for a in buffer:
            if a.label == a.name:
                argument_string.append(f'{a.name}: {a.type}')
            else:
                argument_string.append(f'{a.label} {a.name}: {a.type}')

        return_string = ''
        if self.return_type == 'void':
            return_string = ';'
        else:
            return_string = f' -> {self.return_type};'

        return f'{name}({", ".join(argument_string)}){return_string}'

class Property:
    """
    to be written
    """
    @classmethod
    def create(cls, string):
        attribute_pattern = re.compile(r'@property \((.+?)\) ', re.DOTALL)
        matched = attribute_pattern.match(string)
        attributes = []

        if matched is not None:
            # device by ,
            attributes = matched.group(1).split(',')
            str_ = string.replace(matched.group(0), '')
        else:
            str_ = string.replace('@property ', '')

        type_name_patttern = re.compile(r'(.+?)([\w\d]+);', re.DOTALL)
        matched = type_name_patttern.match(str_)

        return Property(type_=matched.group(1), attributes=attributes, name=matched.group(2))

    def __init__(self, type_, attributes, name):
        self.type = type_
        self.name = name
        self.attributes = attributes

    def write(self):
        # @objc optional var data: Int { get }
        # @objc optional func setData(_ data: Int)
        if 'readonly' in self.attributes:
            return f'    @objc optional var {self.name}: {self.type} {{ get }}'

        temp =  f'    @objc optional var {self.name}: {self.type} {{ get }}\n'
        temp += f'    @objc optional func set{self.name[0].upper() + self.name[1:]}(_ {self.name}: {self.type})'

        return temp

def extract_protocol_name(string):
    name_and_others = string.split(':')
    if len(name_and_others) == 1:
        return (name_and_others[0].strip(), None, [])

    inherits = name_and_others[1].strip()
    protocols = []
    others = name_and_others[1].strip()
    protocol_pattern = re.compile(r'<(.+?)>', re.DOTALL)
    matched = protocol_pattern.search(others)
    if matched is not None:
        protocols = matched.group(1).split(',')

    return (name_and_others[0].strip(), inherits, protocols)

class Interface:
    """
    to be written
    """
    @classmethod
    def create(cls, text):
        protocol_pattern = re.compile(r'^@(protocol|interface)(.+?)$(.+?)@end', re.DOTALL | re.MULTILINE)
        matched = protocol_pattern.match(text)
        type_ = matched[1]
        (name, inherits, protocols) = extract_protocol_name(matched[2])
        lines = matched[3].split('\n')

        filtered = filter(lambda line: len(line) > 0 and line[0] == '-', lines)
        functions = [Function.create(x) for x in filtered]

        filtered = filter(lambda line: len(line) > 0 and line[0] == '@', lines)
        properties = [Property.create(x) for x in filtered]

        return Interface(type_=type_, name=name, inherits=inherits, protocols=protocols, properties=properties, functions=functions)

    def __init__(self, type_, name, inherits, protocols, properties, functions):
        self.type = type_
        self.name = name
        self.inherits = inherits
        self.protocols = protocols
        self.properties = properties
        self.functions = functions

    def dump(self):
        print('---------------------------------')
        print('name: ' + self.name)
        if self.inherits is not None:
            print('inherits: ' + self.inherits)
        print('protocols: ' + str(self.protocols))
        print('properties: ')
        for p in self.properties:
            print('  name: ' + p.name)
            print('  type: ' + p.type)
            print('  attributes: ' + str(p.attributes))
        print('functions: ')
        for f in self.functions:
            print('  returnType: ' + f.returnType)
            print('    arguments: ')
            for a in f.arguments:
                print('      label: ' + a.label)
                if a.type is not None:
                    print('      type: ' + a.type)
                if a.name is not None:
                    print('      name: ' + a.name)

    def write(self):
        temp = ''
        if self.inherits is not None:
            temp = self.inherits
            template=f"""@objc public protocol {self.name} : {temp} {{\n"""
        else:
            template=f"""@objc public protocol {self.name} {{\n"""
        
        for p in self.properties:
            template += p.write() + '\n'

        for f in self.functions:
            template += f.write() + '\n'

        template += '}\n'

        template += f'extension SBObject: {self.name} {{}}\n'

        return template

def extract_types_from_interfaces(interfaces):
    functions = map(lambda x: x.functions, interfaces)
    functions = [item for sublist in functions for item in sublist]
    args = map(lambda x: x.arguments, functions)
    args_from_functions = [item.type for sublist in args for item in sublist]
    args_return_type = list(map(lambda x: x.return_type, functions))

    properties = map(lambda x: x.properties, interfaces)
    properties = [item for sublist in properties for item in sublist]
    args = map(lambda x: x.type, properties)
    args_from_properties = list(args)

    args = args_from_functions + args_from_properties + args_return_type
    args = list(filter(lambda x: x is not None, args))
    args = list(set(args))

    return args

def create_type_convert_dictionary(types):

    extract_pattern = re.compile(r'(.+)<(.+)> \*')

    type_dictionary = {}

    for type_ in types:
        matched = extract_pattern.match(type_)
        if matched is not None:
            extracted_type = matched.group(2).replace('*', '')
            extracted_type = extracted_type.strip()
            type_dictionary[type_.strip()] = f'[{extracted_type}]'
        else:
            extracted_type = type_.replace('*', '')
            extracted_type = extracted_type.strip()
            type_dictionary[type_.strip()] = extracted_type

    return type_dictionary

def main():
    # handle arguments
    parser = argparse.ArgumentParser(description='Convert Objective-C header file to Swift interface.')
    parser.add_argument('header', type=str, help='Objective-C header file path')
    parser.add_argument('swift', type=str, help='Output file path')
    args = parser.parse_args()

    # read header file
    header = open(args.header, 'r', encoding='utf-8')
    header_content = header.read()

    # enum
    enum_pattern = re.compile(r'(^enum (.+?) \{(.+?)\};)', re.DOTALL | re.MULTILINE)
    enum_text_array = enum_pattern.findall(header_content)
    enum_infos = list(map(lambda x: Enum.create(x[0]), enum_text_array))

    # protocol
    protocol_pattern = re.compile(r'(^@(protocol|interface)(.+?)$(.+?)@end)', re.DOTALL | re.MULTILINE)
    protocols = protocol_pattern.findall(header_content)
    interfaces = list(map(lambda x: Interface.create(x[0]), protocols))

    # analye type
    types = extract_types_from_interfaces(interfaces)
    type_dictionary = create_type_convert_dictionary(types)

    # hueristics
    # update dictionary
    type_dictionary['long long'] = 'Int64'
    type_dictionary['long'] = 'Int'
    type_dictionary['id'] = 'Any'
    type_dictionary['BOOL'] = 'Bool'
    type_dictionary['double'] = 'Double'

    # heuristics - some protocols are derived from some objects.
    # search among interfaces
    for interface in interfaces:
        if interface.inherits is not None:
            interface.inherits = interface.inherits.replace('SBObject <MusicGenericMethods>', 'MusicGenericMethods')
        if interface.inherits == 'SBApplication':
            interface.inherits = None

    # hueristics
    # update type in interfaces
    for interface in interfaces:
        for prop in interface.properties:
            prop.type = type_dictionary[prop.type.strip()]   
        for function in interface.functions:
            function.return_type = type_dictionary[function.return_type.strip()]
            for arg in function.arguments:
                if arg.type is not None:
                    arg.type = type_dictionary[arg.type.strip()]

    # output
    with open(args.swift, 'w') as f:
        for e in enum_infos:
            f.write(e.write())

        for i in interfaces:
            f.write(i.write())

    # for e in enum_infos:
    #     print(e.write())

    # for i in interfaces:
    #     print(i.write())

main()
