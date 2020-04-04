---
title: Sweeps
header-includes:
    <link href="styles.css" rel="stylesheet"/>
---

## Sweep

This generates all the parameter sweep space based on provided
input. A specific example can be shown below

```json
{
{"Element" : "Initial Global Quantities", "Name": "SOCS_Binding_Rate", "values" : [1,2,3]},
{"Element" : "Initial Species Values", "Compartments" : "Cytoplasm","Name": "Her4", "values" : [1,2,3]},
{"Element" : "Initial Time", "values" : [1,2,3]},
{"Element" : "Kinetic Parameters", "Reactions" : "01 - HER4 JAK Binding", "ParameterGroup" : "Parameters", "Parameter" : "k1", "values" : [1,2,3]},
{"Element" : "Initial Compartment Sizes", "Compartments" : "Cytoplasm", "values" : [1,2,3]}
}
```

In the above we have a list of parameter specification. The sweep
space will be generated for each element of the above list and
over all possible combinations. This can be done using the
`itertools.product` function as below.

```python
>>> Sweep_Input = [{"Element" : "Initial Global Quantities", \
"Name": "SOCS_Binding_Rate", "values" : [1,2,3]},{"Element" : "Initial Species Values",\
"Compartments" : "Cytoplasm","Name": "Her4", "values" : [1,2,3]},\
{"Element" : "Initial Time", "values" : [1,2,3]},\
{"Element" : "Kinetic Parameters", "Reactions" : "01 - HER4 JAK Binding",\
"ParameterGroup" : "Parameters", "Parameter" : "k1", "values" : [1,2,3]},\
{"Element" : "Initial Compartment Sizes", "Compartments" : "Cytoplasm",\
"values" : [1,2,3]}]
>>> Sweep_List = { elem["Element"] : elem["values"]  for elem in Sweep_Input }
>>> Sweep_List
{'Initial Global Quantities': [1, 2, 3], 'Initial Species
Values': [1, 2, 3], 'Initial Time': [1, 2, 3], 'Initial
Compartment Sizes': [1, 2, 3], 'Kinetic Parameters': [1, 2, 3]}
>>> import itertools
>>> Sweep_List_All = []
>>> for ii, value in enumerate(list(itertools.product(*Sweep_List.values()))):
...     Sweep_List_All.append(dict(zip(Sweep_List.keys(), value)))
... 
>>> Sweep_List_All[:5]
[{'Initial Global Quantities': 1, 'Initial Species Values': 1,
'Initial Time': 1, 'Kinetic Parameters': 1, 'Initial Compartment
Sizes': 1}, {'Initial Global Quantities': 1, 'Initial Species
Values': 1, 'Initial Time': 1, 'Kinetic Parameters': 2, 'Initial
Compartment Sizes': 1}, {'Initial Global Quantities': 1, 'Initial
Species Values': 1, 'Initial Time': 1, 'Kinetic Parameters': 3,
'Initial Compartment Sizes': 1}, {'Initial Global Quantities': 1,
'Initial Species Values': 1, 'Initial Time': 1, 'Kinetic
Parameters': 1, 'Initial Compartment Sizes': 2}, {'Initial Global
Quantities': 1, 'Initial Species Values': 1, 'Initial Time': 1,
'Kinetic Parameters': 2, 'Initial Compartment Sizes': 2}]
```

The list `Sweep_List_All` is the sweep space. Instead of the name
of the parameter type this should just be keyed with the
identifier string or split into two keys `id` and `value`.
