### WORKING WITH BASE MODELS ###
from pydantic import BaseModel

## CREATING MODEL EXTENDED FROM BASE MODEL ##
class MyModel(BaseModel):
    id: int
    name: str
    job: str
    price: int

## CREATING SQL TABLE WITH MODEL ##

from MentoDB import *
# Firstly, we have to initialize a connection with using MentoConnection (same as "sqlite3.Connection")
con = MentoConnection("./database/new.db", check_same_thread=False)

# Then, create a database cursor with connection object.
cursor = Mento(con)

# Now we created a table looking like (id int, name text, job text, price int)
cursor.create("sample_table", model=MyModel)

## USING PRIMARYKEY AND UNIQUE COLUMN MATCHES WHEN CREATING TABLES ##

# PRIMARY KEY

class PrimaryKeySample(BaseModel):
    id: PrimaryKey(int).set_primary()
    name: str
    age: int
    price: int

# Now we created a table looking like (id int primary key, name text, job text, price int)
cursor.create("primary_sample", model=PrimaryKeySample)

# UNIQUE MATCHES

class Sample(BaseModel):
    id: PrimaryKey(int).set_primary()
    name: str
    age: int
    price: int
    check_match: UniqueMatch("id", "name").set_match()

# Now we've a match, if we have to insert some data and these datas protected with UniqueMatch type;
# We give check_model parameter (if we want to check matches), then it will check gaven datas;
# If table has matched data, insert process will be stopped.
cursor.create("unique_matches_sample", model=Sample)

cursor.check_model = Sample

### DATA STATEMENTS ###

# CREATE #
# Creates a table, if table is not exists.
cursor.create("sample", model=Sample)

# Creates a table.
cursor.create("sample", model=Sample, exists_check=False)

# Creates many table (table_name: TableModel)
cursor.create_many(
    dict(first=MyModel, second=PrimaryKeySample, third=Sample)
)

# INSERT #
cursor.insert(
    "sample",
    data=dict(id = 1, name = "fswair", age = 18, price = 4250),
    # if your model has UniqueMatch control and you want to check matches, set a model by check_model keyword argument.
    check_model=Sample
)

# SELECT #

# Returns all rows as list[dict] -> [{id: 1, name: fswair, age: 18, price: 4250}] 
cursor.select("sample")

# Returns all rows matched with where condition. Condition looking like (in SQL);
# "SELECT * FROM TABLE WHERE id = 1 AND name = 'fswair'"
cursor.select("sample", where={
    "id": 1,
    "name": "fswair"
})

# Returns all rows matched with where condition sorted as ORDER BY. Condition looking like (in SQL);
# "SELECT * FROM TABLE WHERE id = 1 AND name = 'fswair' ORDER BY id"
cursor.select("sample", where={
    "id": 1,
    "name": "fswair"
},
order_by="id"
)

# Returns all row's id columns as list[dict] -> [{id: 1}, {id: 2}]
cursor.select("sample", select_column="id")

# Returns all rows matched with lambda filter (lambda arg must be column name)
# Sample Output: list[dict] -> [{id: 3, name: fswair, age: 18, price: 4250}]
cursor.select("sample", filter=lambda id: id % 3 == 0)

# Returns all rows matched with regexp patterns (regexp dict must be one key as column name, value could be pattern or list of pattern.)
# Sample Output: list[dict] -> [{id: 999, name: fswair, age: 18, price: 4250}]
cursor.select("sample", regexp={"id": ["\d{1,3}"] })

# UPDATE #

# Updates the data matched with where condition.
cursor.update("sample", data=dict(id=2, name="fswair", age=19, price=10000), where=dict(id=1))

# Updates all of the data with same value.
cursor.update("sample", data=dict(price=10000), update_all=True)


# DELETE #

# Deletes all of the data matched with where condition.
cursor.delete("sample", where=dict(id=1, age=19))


# Deletes all of the data in table.
cursor.delete("sample", delete_all=True)

# DROP #

# Drops specified table.
cursor.drop("sample")