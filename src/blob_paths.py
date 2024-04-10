class BlobPaths:
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        self.value = value

    def __truediv__(self, other):
        if not isinstance(other, BlobPaths):
            raise ValueError("Operand must be an instance of SlashString")
        return BlobPaths(self.value + '/' + other.value)

    def __repr__(self):
        return f"SlashString('{self.value}')"

    def get_id(self):
        return self.value.split('/')[0]
