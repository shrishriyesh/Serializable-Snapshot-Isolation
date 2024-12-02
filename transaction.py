# transaction.py

class Transaction:
    def __init__(self, transactionID, startTime, is_read_only=False):
        self.id = transactionID
        self.startTime = startTime
        self.is_read_only = is_read_only
        self.read_set = set()
        self.write_set = {}
        self.status = 'active'  # Other statuses: 'committed', 'aborted'
        # Additional attributes as needed

    def read(self, variable_name, sites):
        # Implement read logic
        # For read-only transactions, read the committed value as of startTime
        # For read-write transactions, read the latest committed value
        for site in sites.values():
            if site.is_up and site.has_variable(variable_name):
                value = site.read(self, variable_name)
                if value is not None:
                    self.read_set.add(variable_name)
                    return value
        # If variable is not available, transaction may need to wait
        return None

    def write(self, variable_name, value, sites):
        # Store the write in the transaction's write set
        self.write_set[variable_name] = value
        # Propagate write to all available sites
        for site in sites.values():
            if site.is_up and site.has_variable(variable_name):
                site.write(self, variable_name, value)
        # Handle cases where some sites are down if necessary

    # Additional methods as needed
