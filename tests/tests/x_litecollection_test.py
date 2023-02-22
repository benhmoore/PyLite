# from multiprocessing.sharedctypes import Value
import pytest, sqlite3, os
from lite import *

os.environ['DB_DATABASE'] = 'pytest.sqlite'

# Create models for tests
class User(LiteModel):

    TABLE_NAME = 'users_custom_table_name'
    
    def parent(self):
        return self.belongsTo(User,'user_id')

    def child(self):
        return self.hasOne(User)

    def cars(self):
        return self.belongsToMany(Car)

    def bank_account(self):
        return self.hasOne(Bank_Account)

    def products(self):
        return self.hasMany(Product)

def test_get_length():
    """Tests to see if length of collection can be accurately attained."""

    collection = LiteCollection()
    assert len(collection) == 0

    del collection

def test_add():
    """Tests adding to LiteCollection instance."""

    collection = LiteCollection()

    user_1 = User.create({"username":'ben',"password":'123'})
    user_2 = User.create({"username":'toby',"password":'123'})
    user_3 = User.create({"username":'ike',"password":'123'})

    collection.add(user_1)
    collection.add(user_2)
    collection.add(user_3)
    
    assert collection == LiteCollection([user_1, user_2, user_3])

    del collection

def test_add_duplicate():
    """Tests adding to LiteCollection instance."""

    collection = LiteCollection()

    user_1 = User.create({"username":'ben',"password":'123'})

    collection.add(user_1)
    
    with pytest.raises(DuplicateModelInstance):
        collection.add(user_1)

    del collection

def test_remove():
    """Tests removing from LiteCollection instance."""

    collection = LiteCollection()

    user_1, user_2, user_3 = User.all()[:3]

    collection.add(user_1)
    collection.add(user_2)
    collection.add(user_3)

    collection.remove(user_1)
    collection.remove(user_3)
    
    assert collection == LiteCollection([user_2])

def test_equality():
    """Tests comparisons of LiteCollection instances."""

    c_1 = LiteCollection()

    user_1, user_2, user_3 = User.all()[:3]

    c_1.add(user_1)
    c_1.add(user_2)
    c_1.add(user_3)

    c_2 = LiteCollection()
    c_2.add(user_1)
    c_2.add(user_2)
    c_2.add(user_3)

    assert c_1 == c_2
    
def test_contains():
    """Tests the 'in' operator of LiteCollection instances."""

    user_1, user_2, user_3 = User.all()[:3]

    c_1 = LiteCollection([user_1, user_3])

    c_1.remove(user_1)

    assert user_1 not in c_1
    assert user_2 not in c_1
    assert user_3 in c_1
    
    # Using primary key (id) value
    assert 4 in c_1

def test_fresh():

    user_1, user_2, user_3 = User.all()[:3]

    c_1 = LiteCollection([user_1, user_2, user_3])

    user_1_copy = User.all()[:1][0]
    user_1_copy.password = 'changed'
    user_1_copy.save()

    assert user_1_copy.password != c_1[0].password

    c_1.fresh()

    assert user_1_copy.password == c_1[0].password

def test_intersection():
    user_1, user_2, user_3, user_4 = User.all()[:4]

    c_1 = LiteCollection([user_1, user_2, user_3])
    c_2 = LiteCollection([user_1, user_2, user_4])

    assert c_2.intersection(c_1) == LiteCollection([user_1, user_2])

def test_difference():
    user_1, user_2, user_3, user_4 = User.all()[:4]

    c_1 = LiteCollection([user_1, user_2, user_3])
    c_2 = LiteCollection([user_1, user_2, user_4])

    assert c_2.difference(c_1) == LiteCollection([user_4])

def test_where():

    users = User.all()

    assert len(users.where([
        ['id','=',2]
    ])) == 1

    assert len(users.where([
        ['id','!=',11]
    ])) == 10


    assert len(users.where([
        ['id','>',10]
    ])) == 2

    assert len(users.where([
        ['id','>=',10]
    ])) == 3


    assert len(users.where([
        ['id','<',10]
    ])) == 8

    assert len(users.where([
        ['id','<=',10]
    ])) == 9