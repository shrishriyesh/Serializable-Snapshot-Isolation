import copy
class Transaction:
    def __init__(self, transaction_id, start_time, sites, manager):
        self.transaction_id = transaction_id
        self.start_time = start_time
        self.initial_sites = copy.deepcopy(sites)
        self.variables_write = set()  # set of variables written by this transaction
        self.variables_read = set()  # set of variables read by this transaction
        self.sites_snapshot = copy.deepcopy(sites) # snapshot of the sites at the start of the transaction
        self.is_active = True
        self.manager = manager


    def read(self, variable_name):
        self.variables_read.add(variable_name)
        found = False
        for i in range(1, 11):
            site = self.sites_snapshot[i]
            if site.is_up and variable_name in site.variables:
                try:
                    if len(site.failTime) == 0:
                        print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
                        found = True
                        return
                    else:
                        for failTime in site.failTime:
                            if self.manager.verbose:
                                print(f"failtime: {failTime}")
                                # print all the values that we are checking below in if
                                print(f"site.commitTime[variable_name]: {site.commitTime[variable_name]} < failTime: {failTime} < self.start_time: {self.start_time}")
                            if site.commitTime[variable_name] < failTime < self.start_time:
                                if self.manager.verbose:
                                    print({self.manager.last_commits.get(variable_name, 0)} and {failTime} and {self.start_time})
                                raise Exception(f"Site {site.site_id} failed at {failTime}")

                            print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
                            found = True
                            return
                except Exception as e:
                    pass
            # else:
            #     # else site is down , we check the same as above and instead of reading it at that time we put it in a wait queue.
            #     try:
            #         #last commit time<site failure time<transaction start time
            #         if len(site.failTime) == 0:
            #             print(f"site.commitTime[variable_name]: {site.commitTime[variable_name]} < failTime: {failTime} < self.start_time: {self.start_time}")
            #             print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
            #             self.manager.waiting_transactions[site.site_id].append((self.transaction_id, variable_name))
            #             found = True
            #             break
            #             return
            #         else:
            #             for failTime in site.failTime:
            #                 if site.commitTime[variable_name] < failTime < self.start_time:
            #                     raise Exception(f"Site {site.site_id} failed at {failTime}")

            #                 # print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
            #             self.manager.waiting_transactions[site.site_id].append((self.transaction_id, variable_name))
            #             found = True
            #             break
            #             return
        for i in range(1, 11):
            site = self.manager.sites[i]
            if site.is_up==False and variable_name in site.variables:
                try:
                    #last commit time<site failure time<transaction start time
                    if self.manager.verbose:
                        print(f"failtime: {site.failTime} and {site.site_id}")
                        print(f"len(failTime): {len(site.failTime)}")
                    if len(site.failTime) == 0:
                        if self.manager.verbose:
                            print(f"site.commitTime[variable_name]: {site.commitTime[variable_name]} < failTime: {site.failTime} < self.start_time: {self.start_time}XYZ")
                        print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
                        self.manager.waiting_transactions[site.site_id].append((self.transaction_id, variable_name))
                        found = True
                        return
                    else:
                        for failTime in site.failTime:
                            if self.manager.verbose:
                                print(f"commitTime: {site.commitTime[variable_name]} < failTime: {failTime} < self.start_time: {self.start_time}")
                            if site.commitTime[variable_name] < failTime < self.start_time:
                                raise Exception(f"Site {site.site_id} failed at {failTime}")
                            else:
                                if self.manager.verbose:
                                    print("Adding to waiting transactions")
                                print(f"{self.transaction_id} will read {variable_name} at site {site.site_id} after site recovers")
                                # self.manager.waiting_transactions[site.site_id].append((self.transaction_id, variable_name,i))#saves transaction id, variable name and site id
                                if site.site_id not in self.manager.waiting_transactions:
                                    self.manager.waiting_transactions[site.site_id] = []  # Initialize with an empty list
                                self.manager.waiting_transactions[site.site_id].append((self.transaction_id, variable_name, i))
                                if self.manager.verbose:
                                    print(f"waiting_transactions: {self.manager.waiting_transactions}")
                                found = True
                                return
                            # print(f"{self.transaction_id} reads {variable_name} = {site.variables[variable_name].value} at site {site.site_id}")
                        

                except Exception as e:
                    
                    pass

        #Abort this transaction if the variable is not available in any of the sites
        print(found)
        if found == False:
            print(f"{self.transaction_id} aborts because {variable_name} is not available in any of the sites")
            self.manager.abort_transaction(self.transaction_id)

    def write(self, variable_name, value):
        for i in range(1, 11):
            site = self.sites_snapshot[i]
            #if the site is up and the variable is present in the site then change the value of it
            if site.is_up and variable_name in site.variables:
                site.variables[variable_name].value = value
                self.variables_write.add(variable_name)
                print(f"{self.transaction_id} writes in local snapshot the {variable_name} = {value} at site {site.site_id}")

        #print the state of the sites after writing
        if self.manager.verbose:
            print("After writing:")
            for site in self.sites_snapshot.values():
                print(site)

    # returns the new value of the sites if the transaction is not aborted. Or else it sends the abort signal and returns null
    def commit(self, current_sites):
        for variable_name in self.variables_write:
            last_commit_time = self.manager.last_commits.get(variable_name, -1)
            
            # If some other transaction committed this variable after we started, abort.
            if last_commit_time > self.start_time:
                print(f"{self.transaction_id} aborts because {variable_name} was already committed by another transaction after we started")
                self.abort()
                return None
            
        # Add edges to the serialization graph for this transaction
        for var in self.variables_write:
            # Check if this var exisits in self.manager.overall_writes and add edges to the serialization graph of the transactions
            if var in self.manager.overall_writes:
                for txn, timestamp in self.manager.overall_writes[var]:
                    if txn != self.transaction_id and timestamp < self.manager.time:
                        if txn not in self.manager.serialization_graph:
                            self.manager.serialization_graph[txn] = []
                        if self.transaction_id not in self.manager.serialization_graph[txn]:
                            self.manager.serialization_graph[txn].append([self.transaction_id, "WW"])
                            print(f"Added WW edge from {txn} to {self.transaction_id}")

                            # Check if adding this Edge creates a cycle in the graph
                            if self.manager.detect_cycle():
                                print(f"{self.transaction_id} aborts due to cycle in serialization graph")
                                self.manager.remove_transaction(self.transaction_id)
                                self.abort()
                                return None

            #Do the same for overall reads
            if var in self.manager.overall_reads:
                for txn, timestamp in self.manager.overall_reads[var]:
                    if txn != self.transaction_id and timestamp < self.manager.time:
                        if txn not in self.manager.serialization_graph:
                            self.manager.serialization_graph[txn] = []
                        if self.transaction_id not in self.manager.serialization_graph[txn]:
                            self.manager.serialization_graph[txn].append([self.transaction_id, "RW"])
                            print(f"Added RW edge from {txn} to {self.transaction_id}")

                            # Check if adding this Edge creates a cycle in the graph
                            if self.manager.detect_cycle():
                                print(f"{self.transaction_id} aborts due to cycle in serialization graph")
                                self.manager.remove_transaction(self.transaction_id)
                                self.abort()
                                return None


        for var in self.variables_read:
            if var in self.manager.overall_writes:
                for txn, timestamp in self.manager.overall_writes[var]:
                    if txn != self.transaction_id and timestamp > self.manager.time:
                        if txn not in self.manager.serialization_graph:
                            self.manager.serialization_graph[txn] = []
                        if self.transaction_id not in self.manager.serialization_graph[txn]:
                            self.manager.serialization_graph[txn].append([self.transaction_id, "WR"])
                            print(f"Added WR edge from {txn} to {self.transaction_id}")
                           
                            # Check if adding this Edge creates a cycle in the graph
                            if self.manager.detect_cycle():
                                print(f"{self.transaction_id} aborts due to cycle in serialization graph")
                                self.manager.remove_transaction(self.transaction_id)
                                self.abort()
                                return None

        # If we reach here, we can commit
        print(f"{self.transaction_id} commits")

        # Update last commit times for the variables we wrote
        for variable_name in self.variables_write:
            self.manager.last_commits[variable_name] = self.manager.time

        return self.sites_snapshot
    
    def abort(self):
        self.is_active = False
        print(f"{self.transaction_id} aborts")

    def __repr__(self):
        return f"Transaction {self.transaction_id}"
