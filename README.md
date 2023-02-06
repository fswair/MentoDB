# MentoDB
Sqlite3 based powerful database project.

#### Requirements:
* `Python 3.9.6 or greater version`
* `pydantic` -> `pip install pydantic`
* `pandas` -> `pip install pandas`
* `numpy` -> `pip install numpy`

* Import these two module before start:
```python
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
```

## Working with Base Models
The following code demonstrates how to work with base models in Python using `pydantic` and `dataclasses`.

### _Creating a Model Extended from Base Model_
The following code creates a model named `MyModel` that extends from `BaseModel`:
```python
@dataclass
class MyModel(BaseModel):
    id: int
    name: str
    job: str
    price: int
```
### _Creating a SQL Table with a Model_
Here's an example of how to create a SQL table with the `MyModel` model:
```python
# Initialize a connection with MentoConnection (similar to "sqlite3.Connection")
con = MentoConnection("./database/new.db", check_same_thread=False)

# Create a database cursor with the connection object.
cursor = Mento(con)

# Create a table with the following structure: (id int, name text, job text, price int)
cursor.create("sample_table", model=MyModel)
```
### _Using Primary Key and Unique Column Matches When Creating Tables_
Primary Key:
```python
@dataclass
class PrimaryKeySample(BaseModel):
    id: PrimaryKey(int).set_primary()
    name: str
    age: int
    price: int

# Create a table with the following structure: (id int primary key, name text, age int, price int)
cursor.create("primary_sample", model=PrimaryKeySample)
```
Unique Matches:
```python
@dataclass
class Sample(BaseModel):
    id: PrimaryKey(int).set_primary()
    name: str
    age: int
    price: int
    check_match: UniqueMatch("id", "name").set_match()

# Create a table with unique match control.
cursor.create("unique_matches_sample", model=Sample)

# Set the check_model parameter to check if there are matches.
# If the table has matched data, the insert process will be stopped.
cursor.check_model = Sample
```
## Data Statements
### _Create_
* Create a table if it does not already exist:
```python
cursor.create("sample", model=Sample)
```
* Create a table without checking if it already exists:
```python
cursor.create("sample", model=Sample, exists_check=False)
```
* Create multiple tables:
```python
cursor.create_many(dict(first=MyModel, second=PrimaryKeySample, third=Sample))
```
### _Insert_
```python
cursor.insert(
    "sample",
    data=dict(id=1, name="fswair", age=18, price=4250),
    # If your model has a UniqueMatch control and you want to check matches, set the model with the check_model keyword argument.
    check_model=Sample
    )
```
### _Select_
* Return all rows as a list of dictionaries:
```python
cursor.select("sample")
# Output: [{id: 1, name: fswair, age: 18, price: 4250}]
```
## SELECT
The following are the different methods for returning data from the table using the `select` statement in the `cursor` object:
* `cursor.select("sample")`: Returns all rows as `list[dict]` -> `[{id: 1, name: fswair, age: 18, price: 4250}]`

* `cursor.select("sample", where={"id": 1, "name": "fswair"})`: Returns all rows matched with the where condition. The condition looks like (in SQL): `SELECT * FROM TABLE WHERE id = 1 AND name = 'fswair'`.

* `cursor.select("sample", where={"id": 1, "name": "fswair"}, order_by="id")`: Returns all rows matched with the where condition sorted as `ORDER BY`. The condition looks like (in SQL): `SELECT * FROM TABLE WHERE id = 1 AND name = 'fswair' ORDER BY id`.

* `cursor.select("sample", select_column="id")`: Returns all row's id columns as `list[dict]` -> `[{id: 1}, {id: 2}]`

* `cursor.select("sample", filter=lambda id: id % 3 == 0)`: Returns all rows matched with the lambda filter (lambda arg must be column name). Example output: `list[dict]` -> `[{id: 3, name: fswair, age: 18, price: 4250}]`.

* `cursor.select("sample", regexp={"id": ["\d{1,3}"]})`: Returns all rows matched with regexp patterns (regexp dict must be one key as column name, value could be pattern or list of patterns). Example output: `list[dict]` -> `[{id: 999, name: fswair, age: 18, price: 4250}]`.

### _Response Formatters for Select Statement_
The following are the response formatters for the select statement:
* `cursor.select("table", as_json=True)`: Returns data as JSON.

* `cursor.select("table", as_dataframe=True)`: Returns data as a DataFrame (using Pandas).

* `cursor.select("table", as_dataframe=True).to_csv()`: Returns data as a CSV file.

* `cursor.select("table", model=Sample, as_model=True)`: Returns object list (accessible with attributes).
## UPDATE
The following updates the data matched with the where condition:
```python
cursor.update(
    "sample",
    set_data=dict(name="fswair-up", age=20),
    where={"id": 1, "name": "fswair"}
    )
```
