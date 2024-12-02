# operation.py

from enum import Enum

class OperationType(Enum):
    READ = 'READ'
    WRITE = 'WRITE'

class Operation:
    """
    This class represents a read or write operation.
    """

    def __init__(self, timestamp, transaction_id, variable_id, operation_type, value=None):
        self.timestamp = timestamp              # The time at which the operation was issued
        self.transaction_id = transaction_id    # ID of the transaction performing the operation
        self.variable_id = variable_id          # ID of the variable being accessed
        self.operation_type = operation_type    # OperationType.READ or OperationType.WRITE
        self.value = value                      # Value to write (for write operations)

    def get_timestamp(self):
        """
        Gets the timestamp of the operation.
        """
        return self.timestamp

    def get_transaction_id(self):
        """
        Gets the transaction ID associated with the operation.
        """
        return self.transaction_id

    def get_variable_id(self):
        """
        Gets the variable ID involved in the operation.
        """
        return self.variable_id

    def get_operation_type(self):
        """
        Gets the type of the operation (READ or WRITE).
        """
        return self.operation_type

    def get_value(self):
        """
        Gets the value associated with the operation.
        """
        return self.value

    def set_value(self, value):
        """
        Sets the value of the operation (used for setting read values).
        """
        if self.operation_type == OperationType.READ:
            self.value = value
