# variable.py

class Variable:
    def __init__(self, name, initial_value):
        self.name = name
        self.committed_value = initial_value
        self.pending_writes = {}  # transaction_id: value
        self.versions = [(0, initial_value)]  # List of tuples (commit_time, value)
        # Additional attributes as needed

    def read(self, transaction_start_time):
        # Return the latest committed value before transaction_start_time
        for commit_time, value in reversed(self.versions):
            if commit_time <= transaction_start_time:
                return value
        # If no version is available, return None
        return None

    def write(self, transaction_id, value):
        # Store the pending write
        self.pending_writes[transaction_id] = value

    def commit(self, transaction_id, value):
        # Commit the pending write
        if transaction_id in self.pending_writes:
            # Update the committed value
            self.committed_value = value
            # Add the new version with the current time
            self.versions.append((transaction_id, value))
            # Remove from pending writes
            del self.pending_writes[transaction_id]

    # Additional methods as needed
