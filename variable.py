# variable.py

class Variable:
    def __init__(self, variable_id):
        self.id = variable_id
        initial_value = 10 * variable_id
        self.value_to_commit = initial_value
        self.transaction_id_to_commit = None
        self.last_committed_value = initial_value
        self.committed_values = {0: initial_value}  # timestamp -> value
        self.is_readable = True

    def get_id(self):
        return self.id

    def get_value_to_commit(self):
        return self.value_to_commit

    def get_transaction_id_to_commit(self):
        return self.transaction_id_to_commit

    def get_last_committed_value(self):
        return self.last_committed_value

    def get_last_committed_value_before(self, timestamp):
        # Implement logic to retrieve the last committed value before a given timestamp
        pass  # Fill in with appropriate logic

    def is_readable(self):
        return self.is_readable

    def set_value_to_commit(self, value):
        self.value_to_commit = value

    def set_transaction_id_to_commit(self, transaction_id):
        self.transaction_id_to_commit = transaction_id

    def fail(self):
        self.is_readable = False

    def recover(self):
        # If variable ID is odd (non-replicated), it's immediately readable upon recovery
        if self.id % 2 != 0:
            self.is_readable = True
        # Else, remains non-readable until a new value is committed

    def commit(self, timestamp):
        self.last_committed_value = self.value_to_commit
        self.committed_values[timestamp] = self.last_committed_value
        self.is_readable = True

    def __str__(self):
        return f"x{self.id}: {self.last_committed_value}"
