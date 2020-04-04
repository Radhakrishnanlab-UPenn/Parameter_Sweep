---
title: Change
header-includes:
    <link href="styles.css" rel="stylesheet"/>
---

## Change

This script changes a specific parameter in a Copasi file.
The Copasi elements which need to be changed have the following
form

```xml
<ModelParameterGroup cn="String=Initial Species Values" type="Group">
  <ModelParameter cn="CN=Root,Model=ErbB4 JAK2 STAT5
  Yamada,Vector=Compartments[Cytoplasm],Vector=Metabolites[Her4]"
  value="6022141790000000" type="Species"
  simulationType="reactions"/>
```

The easiest way to locate such an element is to generate the
identifier string `cn` dynamically based on the name of the
model, compartment name and parameter types. The general format
of the identifiers are as below

Species - `CN=Root,Model=%s,Vector=Compartments[%s],Vector=Metabolites[%s]`
Compartments - `CN=Root,Model=%s,Vector=Compartments[%s]`
Globals - `CN=Root,Model=%s,Vector=Values[%s]`
Kinetic Parameters - `CN=Root,Model=%s,Vector=Reactions[%s],ParameterGroup=%s,Parameter=%s`

The placeholders indicated by `%s` need to be provided by the
user from which the function can construct the string. The model
name can be obtained from the file itself.

This is done in two stages

1. `Generate_Id()` This function generates id for a specific
   parameter type using information from Copasi file
2. `Get_Parameter()` Obtains the current value of target
   parameter
3. `Set_Parameter()` Changes the value of the provided
   parameter.
