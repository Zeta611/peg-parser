import re

sample_json = """{
    "version": 17,
    "bundles": [
        { "name" : "org.graalvm.component.installer.Bundle" },
        { "name" : "org.graalvm.component.installer.commands.Bundle" },
        { "name" : "org.graalvm.component.installer.remote.Bundle" },
        { "name" : "org.graalvm.component.installer.os.Bundle" }
    ]
}"""


class Parser:
    def __init__(self, input: str):
        self.input = input
        self.pos = 0

    def parse(self) -> bool:
        return self.parse_value()

    # Lex
    def skip_ws(self) -> None:
        while self.pos < len(self.input) and self.input[self.pos] in [" ", "\n"]:
            self.pos += 1

    def parse_string(self) -> bool:
        if self.input[self.pos] != '"':
            return False
        try:
            last = self.input[self.pos + 1 :].index('"')
        except ValueError:
            return False
        self.pos += last + 2
        self.skip_ws()
        return True

    def parse_number(self) -> bool:
        match = re.search(r"\D", self.input[self.pos :])
        if match:
            num_len = match.start()
            self.pos += num_len
            return num_len > 0
        else:
            self.pos = len(self.input)
            return True

    def parse_char(self, c: str) -> bool:
        if self.pos >= len(self.input):
            return False
        if self.input[self.pos] != c:
            return False
        self.pos += 1
        self.skip_ws()
        return True

    # Parse
    # value ::= string / number / object / array
    # object ::= "{" (PAIR ("," PAIR)* )? "}"
    # pair ::= string ":" value
    # array ::= "[" (value ("," value)* )? "]"

    # value ::= string / number / object / array
    def parse_value(self) -> bool:
        return (
            self.parse_string()
            or self.parse_number()
            or self.parse_object()
            or self.parse_array()
        )

    # object ::= "{" (pair ("," pair)* )? "}"
    def parse_object(self) -> bool:
        pos = self.pos
        if self.parse_char("{") and self.parse_pairs() and self.parse_char("}"):
            return True
        self.pos = pos
        return False

    # (pair ("," pair)* )?
    def parse_pairs(self) -> bool:
        if self.parse_pair():
            self.parse_pair_tails()
        return True

    # pair ::= string ":" value
    def parse_pair(self) -> bool:
        pos = self.pos
        if self.parse_string() and self.parse_char(":") and self.parse_value():
            return True
        self.pos = pos
        return False

    # ("," pair)*
    def parse_pair_tails(self) -> bool:
        while True:
            pos = self.pos
            if not (self.parse_char(",") and self.parse_pair()):
                self.pos = pos
                return True

    # array ::= "[" (value ("," value)* )? "]"
    def parse_array(self) -> bool:
        pos = self.pos
        if self.parse_char("[") and self.parse_values() and self.parse_char("]"):
            return True
        self.pos = pos
        return False

    # (value ("," value)* )?
    def parse_values(self) -> bool:
        if self.parse_value():
            self.parse_value_tails()
        return True

    # ("," value)*
    def parse_value_tails(self) -> bool:
        while True:
            pos = self.pos
            if not (self.parse_char(",") and self.parse_value()):
                self.pos = pos
                return True


parser = Parser(sample_json)
print(parser.parse())
