import cplex

"""Create a modeling problem instance"""

model = cplex.Cplex()

"""Read CSV"""

import pandas as pd
import numpy as np

budget = 150
need_demand = {"beverages": 2, "carbs": 2.5, "cheese": 0.4, "breakfast": 0.3}
demand = [2, 2.5, 0.4, 0.3]
distance_limit = 1600

df_products = pd.read_excel("products.xlsx",engine='openpyxl')
df_distance = pd.read_excel("distance.xlsx",engine='openpyxl')
d = list([list(df_distance["House"]), list(df_distance["Market A"]), list(df_distance["Market B"]), list(df_distance["Market C"]), list(df_distance["Market D"])])


mp = np.zeros((45, 4))

for product, market in enumerate(list(df_products["Market"])):
  if market == 'A':
    mp[product][0] = 1
  elif market == 'B':
    mp[product][1] = 1
  elif market == 'C':
    mp[product][2] = 1
  else:
    mp[product][3] = 1

cp = np.zeros((45, 4))

for product, category in enumerate(list(df_products["Need"])):
  if category == 'Beverages':
    cp[product][0] = 1
  elif category == 'Carbodydrates':
    cp[product][1] = 1
  elif category == 'Cheese':
    cp[product][2] = 1
  else:
    cp[product][3] = 1

"""PART D"""

part_d_i = 22
part_d_j = 26

E = 1 # constant

satisfaction = list(df_products["Satisfaction"])

price = list(df_products["Price"])
price.append(1)
for i in range(1, 31):
  price.append(0)

amount = list(df_products["Amount per Packet"])
for i in range(len(amount)):
  amount[i] = float(amount[i][:-2])

print(satisfaction)

"""Coefficients of the objective function"""

satisfaction.append(E)
for i in range(1, 31):
  satisfaction.append(0)
objective = satisfaction
print(objective)

"""Bounds"""

lower_bounds = [.0] * 76
upper_bounds = [cplex.infinity] * 46
for i in range(1, 31):
  upper_bounds.append(1)

"""Variables"""

variable_names = ["X{}".format(i) for i in range(1, 46)]
variable_names.append("L")

for i in range(1, 6):
  for j in range(1, 6):
    variable_names.append("t" + str(i) + str(j))

for i in range(1, 5):
  variable_names.append("z" + str(i))

variable_names.append("z_d")

variable_types = ['I'] * 46
for i in range(1, 31):
  variable_types.append('B')



model.variables.add(obj=objective, lb=lower_bounds, ub= upper_bounds, names= variable_names, types= variable_types)

"""Objective Function"""

#It is a max problem
model.objective.set_sense(model.objective.sense.maximize)

"""Constraints"""

# Constraint names
constraint_names = ['cost', 'demand_bev', "demand_carb", "demand_cheese",  
                    "demand_break", "distance", "marketa", "marketb", "marketc",
                    "marketd", "ifa", "ifb", "ifc", "ifd", "house"] #one constraint

dist_arr = ["dist{}".format(i) for i in range(1, 11)]
for dist in dist_arr:
  constraint_names.append(dist)

ii_arr = ["ii{}".format(i) for i in range(1, 6)]
for ii in ii_arr:
  constraint_names.append(ii)

return_arr = ["return{}".format(i) for i in range(1, 6)]
for ii in return_arr:
  constraint_names.append(ii)

once_arr = ["once{}".format(i) for i in range(1, 6)]
for ii in once_arr:
  constraint_names.append(ii)

constraint_names.append("either_i_j")
constraint_names.append("or_i_j")

# bev constraints
bev_amount = [0] * 76
carb_amount = [0] * 76
cheese_amount = [0] * 76
break_amount = [0] * 76

bev_amount[:45] = cp[:,0] * amount
carb_amount[:45] = cp[:,1] * amount
cheese_amount[:45] = cp[:,2] * amount
break_amount[:45] = cp[:,3] * amount

# market constraints
market_a = [0] * 76
market_b = [0] * 76
market_c = [0] * 76
market_d = [0] * 76

market_a[:45] = mp[:,0] 
market_b[:45] = mp[:,1] 
market_c[:45] = mp[:,2] 
market_d[:45] = mp[:,3] 

market_a[-5] = -1 * budget
market_b[-4] = -1 * budget
market_c[-3] = -1 * budget
market_d[-2] = -1 * budget

# if additional constraints (market)
if_a = [0] * 76
if_b = [0] * 76
if_c = [0] * 76
if_d = [0] * 76

for i in range(5):
  for j in range(5):
    if i == 1 or j == 1:
      if_a[46 + (i * 5) + j] = -1
    if i == 2 or j == 2:
      if_b[46 + (i * 5) + j] = -1
    if i == 3 or j == 3:
      if_c[46 + (i * 5) + j] = -1
    if i == 4 or j == 4:
      if_d[46 + (i * 5) + j] = -1

if_a[-5] = budget
if_b[-4] = budget
if_c[-3] = budget
if_d[-2] = budget

# distance return constraint
dist_mat = np.zeros((10, 76))

for i in range(5):
  for j in range(5):
    if (i == 1 and j == 0) or (i == 0 and j == 1):
      dist_mat[0][46 + (i * 5) + j] = 1
    if (i == 2 and j == 0) or (i == 0 and j == 2):
      dist_mat[1][46 + (i * 5) + j] = 1
    if (i == 3 and j == 0) or (i == 0 and j == 3):
      dist_mat[2][46 + (i * 5) + j] = 1
    if (i == 4 and j == 0) or (i == 0 and j == 4):
      dist_mat[3][46 + (i * 5) + j] = 1
    if (i == 1 and j == 2) or (i == 2 and j == 1):
      dist_mat[4][46 + (i * 5) + j] = 1
    if (i == 1 and j == 3) or (i == 3 and j == 1):
      dist_mat[5][46 + (i * 5) + j] = 1
    if (i == 1 and j == 4) or (i == 4 and j == 1):
      dist_mat[6][46 + (i * 5) + j] = 1
    if (i == 2 and j == 3) or (i == 3 and j == 2):
      dist_mat[7][46 + (i * 5) + j] = 1
    if (i == 2 and j == 4) or (i == 4 and j == 2):
      dist_mat[8][46 + (i * 5) + j] = 1
    if (i == 3 and j == 4) or (i == 4 and j == 3):
      dist_mat[9][46 + (i * 5) + j] = 1

dist_mat2 = list()
for i in range(10):
  dist_mat2.append([variable_names, dist_mat[i]])

# house constraint
house = [0] * 76

for i in range(5):
  for j in range(5):
    if i == 0 or j == 0:
      house[46 + (i * 5) + j] = 1

# enter a market only once constraint
once_mat = np.zeros((5, 76))

for i in range(5):
  for j in range(5):
    for k in range(5):
      if (i == k or j == k) and i != j:
        once_mat[k][46 + (i * 5) + j] = 1

once_mat2 = list()
for i in range(5):
  once_mat2.append([variable_names, once_mat[i]])

# make sure we leave the place we enter constraint
return_mat = np.zeros((5, 76))

for i in range(5):
  for j in range(5):
    for k in range(5):
      if i == k and i != j:
        return_mat[k][46 + (i * 5) + j] = 1
      if j == k and i != j:
        return_mat[k][46 + (i * 5) + j] = -1

return_mat2 = list()
for i in range(5):
  return_mat2.append([variable_names, return_mat[i]])

# ii constraint
ii_mat = np.zeros((5, 76))

for i in range(5):
  for j in range(5):
    if i == j:
      ii_mat[i][46 + (i * 5) + j] = 1

ii_mat2 = list()
for i in range(5):
  ii_mat2.append([variable_names, ii_mat[i]])

#part d either or constraints
#T22 <= Mz
#T26 <= M(1 - z)

#T22 - Mz <= 0
d_either = [0] * 76
d_either[part_d_i - 1] = 1
d_either[-1] = -1 * budget
print(d_either)
#T26 + Mz <= M
d_or = [0] * 76
d_or[part_d_j - 1] = 1
d_or[-1] = budget
print(d_or)

# constraints with variable names
cost_constraint = [variable_names, price]
d_bev_const = [variable_names, bev_amount]
d_carb_const = [variable_names, carb_amount]
d_cheese_const = [variable_names, cheese_amount]
d_break_const = [variable_names, break_amount]

dist_const = np.zeros((76))
for i in range(5):
  for j in range(5):
    dist_const[46 + j + (i * 5)] = d[i][j]

distance_const = [variable_names, dist_const]

a_const = [variable_names, market_a]
b_const = [variable_names, market_b]
c_const = [variable_names, market_c]
d_const = [variable_names, market_d]

ifa_const = [variable_names, if_a]
ifb_const = [variable_names, if_b]
ifc_const = [variable_names, if_c]
ifd_const = [variable_names, if_d]

house_const = [variable_names, house]

d_either_const = [variable_names, d_either]
d_or_const = [variable_names, d_or]

# constraints array
constraints = [cost_constraint, d_bev_const, d_carb_const, d_cheese_const, 
               d_break_const, distance_const, a_const, b_const, c_const, 
               d_const, ifa_const, ifb_const, ifc_const, ifd_const, house_const]
              
for const in dist_mat2:
  constraints.append(const)

for ii in ii_mat2:
  constraints.append(ii)

for returnx in return_mat2:
  constraints.append(returnx)

for once in once_mat2:
  constraints.append(once)

constraints.append(d_either_const)
constraints.append(d_or_const)

rhs = [budget, demand[0], demand[1], demand[2], demand[3], distance_limit, 
       0, 0, 0, 0, budget - 1, budget - 1, budget - 1, budget - 1, 2, 1, 1, 1, 1,
       1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, budget]

constraint_senses = ['L', 'G', 'G', 'G', 'G', "L", "L", "L", "L", "L", "L", 
                     "L", "L", "L", "E", "L", "L", "L", "L", "L", "L", "L", "L",
                     "L", "L", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E",
                     "L", "L", "L", "L", "L", "L", "L"]

model.linear_constraints.add(lin_expr= constraints, senses= constraint_senses, rhs= rhs, names= constraint_names)

"""Solution"""

model.solve()
print("Obj Value:",model.solution.get_objective_value())
print("Values of Decision Variables:",model.solution.get_values())
model.solution.write('IP_solution_d.txt') #creates a new file and stores the attributes
                                  #of the solution in a written format

