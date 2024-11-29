# database.py

import sys
import re
from transaction_manager import TransactionManager

class Database:
    def __init__(self):
        self.transaction_manager = TransactionManager()
        self.timeStamp = 1

    def run(self):
        # Check if a filename was provided as a command-line argument
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            with open(filename, 'r') as file:
                lines = file.readlines()
        else:
            # Read from standard input if no file is provided
            lines = sys.stdin.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                # Empty line indicates time advancement
                self.timeStamp += 1
                continue

            # Split the line into tokens based on '(', ')', ',', and whitespace
            tokens = re.split(r'[\(\),\s]+', line)
            option = tokens[0]

            if option == 'begin':
                transaction = tokens[1]
                transactionID = int(transaction[1:])  # Extract the number after 'T'
                self.transaction_manager.begin(transactionID, self.timeStamp)
            elif option == 'beginRO':
                transaction = tokens[1]
                transactionID = int(transaction[1:])
                self.transaction_manager.beginRO(transactionID, self.timeStamp)
            elif option == 'R':
                transactionID = int(tokens[1][1:])
                variableId = int(tokens[2][1:])
                self.transaction_manager.read(transactionID, variableId, self.timeStamp)
            elif option == 'W':
                transactionID = int(tokens[1][1:])
                variableId = int(tokens[2][1:])
                value = int(tokens[3])
                self.transaction_manager.write(transactionID, variableId, value, self.timeStamp)
            elif option == 'fail':
                siteID = int(tokens[1])
                self.transaction_manager.fail(siteID)
            elif option == 'recover':
                siteID = int(tokens[1])
                self.transaction_manager.recover(siteID)
            elif option == 'end':
                transaction = tokens[1]
                transactionID = int(transaction[1:])
                self.transaction_manager.end(transactionID, self.timeStamp)
            elif option == 'dump':
                self.transaction_manager.dump()
            else:
                # Handle unrecognized commands if necessary
                print(f"Unrecognized command: {line}")
            # Increment the timestamp after each command
            self.timeStamp += 1

if __name__ == '__main__':
    db = Database()
    db.run()
