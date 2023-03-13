class ArbitraryEvent:
    def __init__(self, name, body, required_acl=None):
        self.name = name
        self._body = dict(body)
        if required_acl:
            self.required_acl = required_acl

    def marshal(self):
        return self._body

    def __eq__(self, other):
        return (
            self.name == other.name
            and self._body == other._body
            and self.required_acl == other.required_acl
        )

    def __ne__(self, other):
        return self != other
