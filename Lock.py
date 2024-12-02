# lock.py

from enum import Enum

class LockType(Enum):
    READ_LOCK = 1
    WRITE_LOCK = 2

class Lock:
    """
    This class represents a lock for a variable.
    """

    def __init__(self, transaction_id, variable_id, lock_type):
        self.transaction_id = transaction_id  # ID of the transaction holding the lock
        self.variable_id = variable_id        # ID of the variable the lock is on
        self.type = lock_type                 # Type of lock: READ_LOCK or WRITE_LOCK

    def get_transaction_id(self):
        """
        Gets the transaction ID.
        """
        return self.transaction_id

    def get_variable_id(self):
        """
        Gets the variable ID.
        """
        return self.variable_id

    def get_type(self):
        """
        Gets the lock type.
        """
        return self.type

    def promote_lock_type(self):
        """
        Promotes the lock to a write lock.
        """
        self.type = LockType.WRITE_LOCK
