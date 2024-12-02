# data_manager.py

from variable import Variable
from lock_manager import LockManager
from transaction import TransactionType
from operation import OperationType, Operation
from typing import List

class DataManager:
    """
    This class provides the storage of variables and manages their locks for a certain site.
    """

    VARIABLE_COUNT = 20  # Total number of variables

    def __init__(self, site_id):
        self.id = site_id
        self.is_active = True
        self.variables = {}       # variable_id -> Variable instance
        self.lock_managers = {}   # variable_id -> LockManager instance
        self.initialize_variables()

    def initialize_variables(self):
        """
        Initializes variables and lock managers for the site based on replication rules.
        """
        for i in range(1, self.VARIABLE_COUNT + 1):
            # Variables with even IDs are replicated at all sites
            # Variables with odd IDs are stored at one site: site_id = (variable_id % 10) + 1
            if i % 2 == 0 or (i % 10) + 1 == self.id:
                self.variables[i] = Variable(i)
                self.lock_managers[i] = LockManager(i)

    def get_id(self):
        """
        Gets the site ID.
        """
        return self.id

    def is_active(self):
        """
        Returns whether the site is active.
        """
        return self.is_active

    def contains_variable(self, variable_id):
        """
        Returns whether the site is holding a variable.
        :param variable_id: Variable ID
        :return: Boolean
        """
        return variable_id in self.variables

    def can_read(self, transaction_type, operation):
        """
        Returns whether a transaction can read a variable.
        :param transaction_type: TransactionType.READ_ONLY or TransactionType.READ_WRITE
        :param operation: Operation object
        :return: Boolean
        """
        variable_id = operation.variable_id
        if not self.is_active or variable_id not in self.variables:
            return False
        variable = self.variables[variable_id]
        if not variable.is_readable:
            return False
        if transaction_type == TransactionType.READ_WRITE:
            lock_manager = self.lock_managers[variable_id]
            return lock_manager.can_acquire_lock(operation.operation_type, operation.transaction_id)
        return True  # Read-only transactions can read if variable is readable

    def read(self, transaction_type, timestamp, operation):
        """
        Reads a value.
        :param transaction_type: TransactionType
        :param timestamp: Timestamp of the transaction
        :param operation: Operation object
        :return: Value read or None if read cannot be performed
        """
        variable_id = operation.variable_id
        if operation.operation_type == OperationType.READ and self.can_read(transaction_type, operation):
            variable = self.variables[variable_id]
            if transaction_type == TransactionType.READ_ONLY:
                return self.read_by_read_only_transaction(timestamp, operation, variable)
            else:
                lock_manager = self.lock_managers[variable_id]
                lock_manager.acquire_lock(operation.operation_type, operation.transaction_id)
                return self.read_by_read_write_transaction(operation, variable)
        return None  # Indicate that the read cannot be performed

    def read_by_read_only_transaction(self, timestamp, operation, variable):
        """
        Reads a value for a read-only transaction.
        :param timestamp: Transaction start timestamp
        :param operation: Operation object
        :param variable: Variable object
        :return: Value read
        """
        value = variable.get_last_committed_value_before(timestamp)
        operation.set_value(value)
        return value

    def read_by_read_write_transaction(self, operation, variable):
        """
        Reads a value for a read-write transaction.
        :param operation: Operation object
        :param variable: Variable object
        :return: Value read
        """
        if variable.transaction_id_to_commit == operation.transaction_id:
            value = variable.value_to_commit
        else:
            value = variable.last_committed_value
        operation.set_value(value)
        return value

    def can_write(self, transaction_type, operation):
        """
        Returns whether a transaction can write to a variable.
        :param transaction_type: TransactionType
        :param operation: Operation object
        :return: Boolean
        """
        variable_id = operation.variable_id
        if (not self.is_active or transaction_type == TransactionType.READ_ONLY
                or variable_id not in self.variables):
            return False
        lock_manager = self.lock_managers[variable_id]
        return lock_manager.can_acquire_lock(operation.operation_type, operation.transaction_id)

    def write(self, transaction_type, operation):
        """
        Writes to a variable.
        :param transaction_type: TransactionType
        :param operation: Operation object
        """
        variable_id = operation.variable_id
        if operation.operation_type == OperationType.WRITE and self.can_write(transaction_type, operation):
            lock_manager = self.lock_managers[variable_id]
            lock_manager.acquire_lock(operation.operation_type, operation.transaction_id)
            variable = self.variables[variable_id]
            variable.set_value_to_commit(operation.value)
            variable.set_transaction_id_to_commit(operation.transaction_id)

    def get_lock_holders(self, variable_id):
        """
        Gets transaction IDs of lock holders on a variable.
        :param variable_id: Variable ID
        :return: List of transaction IDs
        """
        if variable_id in self.lock_managers:
            return self.lock_managers[variable_id].get_lock_holders()
        return []

    def abort(self, transaction_id):
        """
        Aborts a transaction by releasing its locks.
        :param transaction_id: Transaction ID
        """
        for lock_manager in self.lock_managers.values():
            lock_manager.unlock(transaction_id)

    def commit(self, transaction_id, timestamp):
        """
        Commits a transaction by applying its writes and releasing its locks.
        :param transaction_id: Transaction ID
        :param timestamp: Commit timestamp
        """
        for lock_manager in self.lock_managers.values():
            variable_id = lock_manager.get_variable_id()
            if lock_manager.is_write_locked_by(transaction_id):
                variable = self.variables[variable_id]
                variable.commit(timestamp)
            lock_manager.unlock(transaction_id)

    def dump(self):
        """
        Outputs the committed values of all copies of all variables at this site.
        """
        variable_strings = []
        for i in range(1, self.VARIABLE_COUNT + 1):
            if i in self.variables:
                variable_strings.append(str(self.variables[i]))
        variable_state = ', '.join(variable_strings)
        print(f"site {self.id} - {variable_state}")

    def fail(self):
        """
        Fails this site, making it inactive and handling variable and lock statuses.
        """
        self.is_active = False
        for variable in self.variables.values():
            variable.fail()
        for lock_manager in self.lock_managers.values():
            lock_manager.unlock_all()

    def recover(self):
        """
        Recovers this site, making it active and updating variable statuses.
        """
        self.is_active = True
        for variable in self.variables.values():
            variable.recover()
