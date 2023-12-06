# trade-sin-comm-apis

## Setup

1. Install Python: download from https://www.python.org/downloads/

2. Clone repository from GitHub: https://github.com/saphety-developers/trade-sin-comm-apis.git

## Executing the application 

1. Open command line where the repository was cloned

2. Execute Python commands

- Execution examples  

### SIN: Search documents - command line arguments and sample usage

```python sin-search.py```

### SIN: Search documents in QA environment - output  as CSV format to screen:
```cls && python sin-search.py --user SomeUser --endpoint sin-qa --creation-date-start=2023-11-15 --creation-date-end=2023-12-06 --output-format csv --no-output-header --document-types 1 2 3 4```

### SIN: Search documents in QA environment - output as CSV format to teste.csv file:
```cls && python sin-search.py --user SomeUser --endpoint sin-qa --creation-date-start=2023-11-15 --creation-date-end=2023-12-06 --output-format csv --no-output-header --document-types 1 2 3 4 > teste.csv```
