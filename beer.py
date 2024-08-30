# Beer Game Simulator - programmed in python 3.X by Shpati Koleka, 2024. MIT license.

import random
import matplotlib.pyplot as plt

# --- Modify the parameters below to see the effect --- #

rounds = 54
delivery_time = 2 # This is given in weeks. The minimum is 1.
inventory_cost = 1 # This is the cost of inventory per unit per week
backlog_cost = 5 # This is the cost of backlog per unit per week 
sales_price = 10 # This is the sales price per unit
initial_inventory = 11 # This is the initial inventory
maximum_inventory = 15 # This is the maximum capacity for storing inventory
showinitial = True
showgraphs = True
showtextmoderesults = False
# ----------------------------------------------------- #

results = []
example = [[]]

# --- Defining the customer order examples --- #

# example[0] - randomized demand
random.seed(1985)
for i in range(0, rounds):
    example[0].append(random.randint(4, 8))

# example[1] - 4 units of demand for the first 4 weeks and then 8 units per week thereafter
example.append([4]*4 + [8]*rounds)

# example[2] - 4 units of demand for the first 4 weeks, then 6 units for 4 weeks, then 4 units for 4 weeks, then 4 units thereafter
example.append([4]*4 + [6]*4 + [4]*rounds)

example_case = 1

# -------------------------------------------- #

class Player:
    def __init__(self, role):
        self.role = role
        self.inventory = [initial_inventory]*delivery_time  # Initial inventory
        self.backlog = [0]*delivery_time  # Initial backlog (unfulfilled orders)
        self.received = [4]*delivery_time # Initial amount of received items
        self.fulfilled_order = [4]*delivery_time # Initial fulfilled order
        self.order_incoming = [4]*delivery_time  # Orders incoming to the player
        self.order_outgoing = [4]*delivery_time  # Initial order amount to pass downstream
        self.profit = [self.fulfilled_order[-1]*sales_price-self.inventory[-1]*inventory_cost-self.backlog[-1]*backlog_cost]

    def receive_order(self, amount):
        self.order_incoming.append(amount)

    def fulfill_order(self):
        total_order = self.backlog[-1] + (self.order_incoming[-1])
        if total_order <= self.inventory[-1]:
            self.inventory[-1] = self.inventory[-1] - total_order
            self.fulfilled_order.append(total_order)
            self.backlog.append(0)

            # ---- Here is the logic of the outgoing order included. Modify it to see the effect --- #
            modified_order = self.backlog[-1] + self.order_incoming[-1]
            if maximum_inventory < self.inventory[-1]:
                reduce_order = self.inventory[-1] - maximum_inventory
                modified_order = self.backlog[-1] + self.order_incoming[-1] - reduce_order
                if modified_order < 0:
                    modified_order = 0
            self.order_outgoing.append(modified_order)
        else:
            self.fulfilled_order.append(self.inventory[-1])
            self.backlog.append(total_order - self.inventory[-1])
            self.inventory[-1] = 0

            # ---- Here is the logic of the outgoing order included. Modify it to see the effect --- #
            self.order_outgoing.append(self.backlog[-1] + self.order_incoming[-1])
        if self.order_outgoing[-1] < 0:
            self.order_outgoing = 0

class SupplyChain:
    def __init__(self):
        self.factory = Player("Factory")
        self.distributor = Player("Distributor")
        self.wholesaler = Player("Wholesaler")
        self.retailer = Player("Retailer")
        self.players = [self.factory, self.distributor, self.wholesaler, self.retailer]

    def print_status(self):
        for player in reversed(self.players):
            print(f"{player.role} - Order incoming: {player.order_incoming[-1]}, Units received: {player.received[-1]}, Backlog: {player.backlog[-1]}, Fulfilled order: {player.fulfilled_order[-1]}, Remaining inventory: {player.inventory[-1]}, Order outgoing: {player.order_outgoing[-1]}, Profit: {player.profit[-1]}")

    def play_round(self, customer_demand):
            # Retailer
        self.retailer.received.append(self.wholesaler.fulfilled_order[-delivery_time])
        self.retailer.inventory.append(self.retailer.inventory[-1] + self.retailer.received[-1])
        self.retailer.receive_order(customer_demand)
            # Wholesaler
        self.wholesaler.received.append(self.distributor.fulfilled_order[-delivery_time])
        self.wholesaler.inventory.append(self.wholesaler.inventory[-1] + self.wholesaler.received[-1])
        self.wholesaler.receive_order(self.retailer.order_outgoing[-1])
            # Distributor
        self.distributor.received.append(self.factory.fulfilled_order[-delivery_time])
        self.distributor.inventory.append(self.distributor.inventory[-1] + self.distributor.received[-1])
        self.distributor.receive_order(self.wholesaler.order_outgoing[-1])
            # Factory
        self.factory.received.append(self.factory.order_outgoing[-delivery_time])
        self.factory.inventory.append(self.factory.inventory[-1] + self.factory.received[-1])
        self.factory.receive_order(self.distributor.order_outgoing[-1])

        # Fulfill orders and calculate profit
        for i in self.players:
            i.fulfill_order()
            i.profit.append(i.fulfilled_order[-1]*sales_price - int(i.inventory[-1])*inventory_cost - int(i.backlog[-1])*backlog_cost)

    def print_final(self):

        k = delivery_time
        print("\nBelow are the results of the", rounds, "rounds. Each column represents one round. ")
        for i in reversed(self.players):
            results.append(i.role)
            print("\n[",i.role,"history ]\n")
            results.append(i.order_incoming[k:])
            print("Order incoming:\n", results[-1])
            results.append(i.received[k:])
            print("Units received:\n", results[-1])
            results.append(i.backlog[k:])
            print("Backlog:\n", results[-1])
            results.append(i.fulfilled_order[k:])
            print("Fulfilled order:\n", results[-1])
            results.append(i.inventory[k:])
            print("Remaining inventory:\n", results[-1])
            results.append(i.order_outgoing[k:])
            print("Orders outgoing:\n", results[-1])
            results.append(i.profit[k:])
            print("Profit:\n", results[-1])

        total_profit = 0
        print("\n[ Final results of profitablitily ]\n")
        for i in reversed(self.players):
            print(i.role, "- Profit: ", sum(i.profit))
            total_profit += sum(i.profit)
        print("TOTAL Profit:", total_profit,"\n")

# Run the simulation for the amount of rounds given in the begining of the program
supply_chain = SupplyChain()

if showinitial:
    print("\n[ Initial Conditions ]\n")
    supply_chain.print_status()

for round_num in range(0, rounds):
    customer_demand = example[example_case][round_num]
    
    supply_chain.play_round(customer_demand)

    if showtextmoderesults:
        print("\n[ Round nr.", round_num,":", "Customer Demand =",customer_demand,"]\n")
        supply_chain.print_status()

supply_chain.print_final()

if showgraphs:
    graph_labels = ["Order incoming", "Units received", "Backlog", "Fulfilled order", "Remaining inventory", "Orders outgoing", "Profit"]
    j= 0
    for labels in graph_labels:
        j += 1
        plt.figure(figsize=(12, 6))  # Set the figure size
        plt.plot(results[j+8*0], marker='o', linestyle='-', color='r', label=results[8*0])
        plt.plot(results[j+8*1], marker='o', linestyle='-', color='g', label=results[8*1])
        plt.plot(results[j+8*2], marker='o', linestyle='-', color='b', label=results[8*2])
        plt.plot(results[j+8*3], marker='o', linestyle='-', color='orange', label=results[8*3])
        plt.title(graph_labels[j-1])
        plt.xlabel('Time in weeks')
        plt.ylabel('Quantity')
        plt.legend()
        plt.grid(True)  # Show gridlines
        plt.show()
