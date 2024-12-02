# site.py

from variable import Variable

class Site:
    def __init__(self, site_id):
        self.id = site_id
        self.is_up = True
        self.variables = {}
        self.initialize_variables()
        # Additional attributes as needed

    def initialize_variables(self):
        # Initialize variables based on site rules
        for i in range(1, 21):
            if i % 2 == 0 or (1 + (i % 10)) == self.id:
                variable_name = f"x{i}"
                initial_value = 10 * i
                self.variables[variable_name] = Variable(variable_name, initial_value)

    def fail(self):
        self.is_up = False
        print(f"Site {self.id} is now down.")
        # Additional failure handling as needed
        # Discard uncommitted data, pending transactions, etc.

    def recover(self):
        self.is_up = True
        print(f"Site {self.id} has recovered.")
        # Initialize necessary data structures
        # For replicated data, may need to wait until updated

    def read(self, transaction, variable_name):
        variable = self.variables.get(variable_name)
        if variable:
            if self.is_up:
                return variable.read(transaction.startTime)
            else:
                # Site is down
                return None
        else:
            # Variable not present at this site
            return None

    def write(self, transaction, variable_name, value):
        variable = self.variables.get(variable_name)
        if variable and self.is_up:
            variable.write(transaction.id, value)

    def commit(self, variable_name, value, transaction_id):
        variable = self.variables.get(variable_name)
        if variable and self.is_up:
            variable.commit(transaction_id, value)

    def has_variable(self, variable_name):
        return variable_name in self.variables

    def dump(self):
        if self.is_up:
            print(f"site {self.id} - ", end='')
            vars_state = ', '.join(f"{var_name}: {var.committed_value}" for var_name, var in sorted(self.variables.items()))
            print(vars_state)
        else:
            print(f"site {self.id} is down.")

    # Additional methods as needed
