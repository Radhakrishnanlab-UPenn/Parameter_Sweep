---
title: Run
header-includes:
    <link href="styles.css" rel="stylesheet"/>
---

# Purpose

This script contains functions that sets up and performs
parameter sweep over a specified range of values using a Copasi
based model.

## CreateRunFile

This function takes a root Copasi element and creates a temporary
copy of the file and changes the name of output report file and
also gets the list of headers.

Arguments:

`root` A root Copasi element
`parameter` A dictionary containing the parameters which were
changed in root element

Returns:

`filename` Returns the name of the temporary file which is
created

Example Run:

```python
>>> import run
>>> fileid = run.CreateRunFile(root, parameter)
>>> pprint(fileid)
{'header': ['Time',
            'mRNA_cyt-Cytoplasm',
            'mRNA_nuc-Nucleus',
            'pSTATn_pSTATn-Nucleus',
            'Her4-Cytoplasm',
            'JAK-Cytoplasm',
            'STATc-Cytoplasm',
            'Nrg-Cytoplasm',
            'PPN-Nucleus',
            'SOCS-Cytoplasm',
            'pIFNR-Cytoplasm',
            'pSTATn-Nucleus',
            'RJ-Cytoplasm',
            'IFNRJ-Cytoplasm',
            'IFNRJ2-Cytoplasm',
            'pIFNRJ2-Cytoplasm',
            'PPX-Cytoplasm',
            'STATn-Nucleus'],
 'name': '/tmp/tmpHtjuCh',
 'output': '/tmp/tmpHtjuCh.csv',
 'parameter': {'Paramtype': 'Initial Species Values',
               'substitute': {'compartment': 'Cytoplasm', 'species': 'Her4'},
               'value': 12044283580000000}}
```

## OdeRun

This function calls `CopasiSE` as an external process and updates
the status of the fileid.

Definition:
```
def OdeRun(input_cps, copasipath='CopasiSE'):
```

Arguments:

`input_cps` Name of the input copasi file which is to be run
`copasipath` Path to external copasi executable

Returns:

`out`,`err` Output and error messages from Copasi

Side Effect:

Updates the `status` key of `fileid` if the run is successful.

## Get_Data

This function collects the data from a previous run.

## Cleanup

This function removes the temporary cps and csv files
