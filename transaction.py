# transaction.py

from enum import Enum

class TransactionType(Enum):
    READ_ONLY = 'READ_ONLY'
    READ_WRITE = 'READ_WRITE'

class Transaction:
    """
    This class represents a transaction.
    """

    def __init__(self, transaction_id, timestamp, transaction_type):
        self.id = transaction_id          # Unique identifier for the transaction
        self.timestamp = timestamp        # Start time of the transaction
        self.type = transaction_type      # TransactionType.READ_ONLY or TransactionType.READ_WRITE
        self.is_blocked = False           # Indicates if the transaction is blocked
        self.is_aborted = False           # Indicates if the transaction is aborted
        self.accessed_sites = set()       # Set of site IDs the transaction has accessed

    def get_id(self):
        """
        Gets transaction ID.
        """
        return self.id

    def get_timestamp(self):
        """
        Gets the timestamp of when the transaction started.
        """
        return self.timestamp

    def get_type(self):
        """
        Gets the transaction type.
        """
        return self.type

    def is_blocked(self):
        """
        Returns whether this transaction is blocked.
        """
        return self.is_blocked

    def block(self):
        """
        Sets the transaction to be blocked.
        """
        self.is_blocked = True

    def unblock(self):
        """
        Sets the transaction to be unblocked.
        """
        self.is_blocked = False

    def is_aborted(self):
        """
        Returns whether this transaction is aborted.
        """
        return self.is_aborted

    def set_aborted(self):
        """
        Sets this transaction to be aborted.
        """
        self.is_aborted = True

    def get_accessed_sites(self):
        """
        Gets the sites that this transaction has accessed.
        """
        return self.accessed_sites

    def add_accessed_site(self, site_id):
        """
        Adds a site to the set of accessed sites.
        :param site_id: ID of the site accessed
        """
        self.accessed_sites.add(site_id)

    def has_accessed_site(self, site_id):
        """
        Returns whether this transaction has accessed a certain site.
        :param site_id: ID of the site
        :return: Boolean indicating if the site has been accessed
        """
        return site_id in self.accessed_sites
