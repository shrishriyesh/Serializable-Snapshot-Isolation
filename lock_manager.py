# lock_manager.py

from lock import Lock, LockType

class LockManager:
    """
    This class maintains locks for a single variable on a certain site.
    """

    def __init__(self, variable_id):
        self.variable_id = variable_id
        self.locks = []  # List of Lock objects

    def get_variable_id(self):
        """
        Gets the variable ID.
        """
        return self.variable_id

    def can_acquire_lock(self, operation_type, transaction_id):
        """
        Returns whether a transaction can acquire a lock.
        :param operation_type: 'READ' or 'WRITE'
        :param transaction_id: Transaction ID
        :return: Boolean indicating if the lock can be acquired
        """
        if operation_type == 'READ':
            return self.can_acquire_read_lock(transaction_id)
        elif operation_type == 'WRITE':
            return self.can_acquire_write_lock(transaction_id)
        else:
            return False

    def can_acquire_read_lock(self, transaction_id):
        """
        Returns whether a transaction can acquire a read lock.
        :param transaction_id: Transaction ID
        :return: Boolean
        """
        write_lock = self.get_write_lock()
        if write_lock and write_lock.get_transaction_id() != transaction_id:
            return False
        return True

    def can_acquire_write_lock(self, transaction_id):
        """
        Returns whether a transaction can acquire a write lock.
        :param transaction_id: Transaction ID
        :return: Boolean
        """
        if len(self.locks) > 1:
            return False
        elif len(self.locks) == 1 and self.get_lock(transaction_id) is None:
            return False
        else:
            return True

    def acquire_lock(self, operation_type, transaction_id):
        """
        Adds a lock on a variable.
        :param operation_type: 'READ' or 'WRITE'
        :param transaction_id: Transaction ID
        """
        if operation_type == 'READ':
            self.lock_for_read(transaction_id)
        elif operation_type == 'WRITE':
            self.lock_for_write(transaction_id)

    def lock_for_read(self, transaction_id):
        """
        Adds a read lock on a variable.
        :param transaction_id: Transaction ID
        """
        if self.can_acquire_read_lock(transaction_id):
            transaction_lock = self.get_lock(transaction_id)
            if transaction_lock is None:
                self.locks.append(Lock(transaction_id, self.variable_id, LockType.READ_LOCK))

    def lock_for_write(self, transaction_id):
        """
        Adds a write lock on a variable.
        :param transaction_id: Transaction ID
        """
        if self.can_acquire_write_lock(transaction_id):
            transaction_lock = self.get_lock(transaction_id)
            if transaction_lock is None:
                self.locks.append(Lock(transaction_id, self.variable_id, LockType.WRITE_LOCK))
            else:
                transaction_lock.promote_lock_type()

    def unlock(self, transaction_id):
        """
        Releases locks held by a transaction.
        :param transaction_id: Transaction ID
        """
        self.locks = [lock for lock in self.locks if lock.get_transaction_id() != transaction_id]

    def unlock_all(self):
        """
        Releases all locks.
        """
        self.locks.clear()

    def is_write_locked_by(self, transaction_id):
        """
        Returns whether a transaction holds a write lock.
        :param transaction_id: Transaction ID
        :return: Boolean
        """
        write_lock = self.get_write_lock()
        if write_lock and write_lock.get_transaction_id() == transaction_id:
            return True
        return False

    def get_lock_holders(self):
        """
        Gets all transactions that hold locks on this variable.
        :return: List of transaction IDs
        """
        return [lock.get_transaction_id() for lock in self.locks]

    def get_write_lock(self):
        """
        Gets the write lock if it exists.
        :return: Lock object or None
        """
        for lock in self.locks:
            if lock.get_type() == LockType.WRITE_LOCK:
                return lock
        return None

    def get_lock(self, transaction_id):
        """
        Gets the lock a transaction holds if it exists.
        :param transaction_id: Transaction ID
        :return: Lock object or None
        """
        for lock in self.locks:
            if lock.get_transaction_id() == transaction_id:
                return lock
        return None
