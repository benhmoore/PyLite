import pytest, sqlite3, os
from lite.litemodel import LiteModel
from lite.litetable import LiteTable

# os.environ['DB_DATABASE'] = 'tests_database.db'

# Setup database
test_db = 'tests_database.db'
try:
    os.remove('tests_database.db')
except Exception: pass

LiteTable.create_database(test_db)

# Create models for tests
class User(LiteModel):
    
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

class Car(LiteModel):
    
    def owners(self):
        return self.belongsToMany(User)

class Bank_Account(LiteModel):
    
    def holder(self):
        return self.belongsTo(User)

class Product(LiteModel):
    
    def owner(self):
        return self.belongsTo(User)


# Create tables for tests - - - - -

# Users table
LiteTable.create_table(test_db, 'users', {
    'username': 'TEXT',
    'password': 'TEXT',
    'user_id': 'INTEGER'   
},"id",{
    'user_id':['users','id']
})

# Cars table
# A car can belong to  one or more people, and one person may own multiple cars
LiteTable.create_table(test_db, 'cars', {
    'make': 'TEXT',
    'model': 'TEXT',
})

# Pivot table
LiteTable.create_table(test_db, 'car_user', {
    'cid': 'INTEGER',
    'uid': 'INTEGER',
},"id",{
    "cid":['cars','id'],
    "uid":['users','id']
})

# Bank Account table
LiteTable.create_table(test_db, 'bank_accounts',{
    'account_number': 'INTEGER',
    'routing_number': 'INTEGER',
    'user_id': 'INTEGER',
},"id",{
    "user_id":['user','id']
})

# Products table
LiteTable.create_table(test_db, 'products',{
    'manufacturer': 'TEXT',
    'user_id': 'INTEGER'
},"id",{
    "user_id":['user','id']
})

# Test .create()
@pytest.mark.parametrize("columns, expected", [
    ({
        'username':'john',
        'password':'123'
    }, 1),
    ({
        'username':'jane',
        'password':'123'
    }, 2),
])
def test_create_users(columns, expected):
    user = User.create(columns)
    assert len(user.table.select([])) == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'make':'VW',
        'model':'Jetta'
    }, 1),
    ({
        'make':'Toyota',
        'model':'Sequoia'
    }, 2),
])
def test_create_cars(columns, expected):
    car = Car.create(columns)
    assert len(Car.all()) == expected
    assert car.id == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'account_number':124123,
        'routing_number':124123
    }, 1),
    ({
        'account_number':999999,
        'routing_number':999999
    }, 2),
])
def test_create_bank_accounts(columns, expected):
    bankAccount = Bank_Account.create(columns)
    assert len(Bank_Account.all()) == expected

@pytest.mark.parametrize("columns, expected", [
    ({
        'manufacturer':'Apple, Inc.',
    }, 1),
    ({
        'manufacturer':'Dell, Inc.',
    }, 2),
])

def test_create_products(columns, expected):
    product = Product.create(columns)
    print(product.id)
    assert len(Product.all()) == expected

# Test .attach() and all relationships
def test_attach():
    user_a = User.findOrFail(1)
    user_b = User.findOrFail(2)

    car_1 = Car.all().where([['make','=','VW']])[0]
    bank_acc = Bank_Account.all().where([['account_number','>',125000]])[0]

    product_a = Product.findOrFail(1)
    product_b = Product.findOrFail(2)

    user_b.attach(user_a)
    user_b.attach(car_1)
    
    user_a.attach(bank_acc)

    user_b.attach(product_a)
    user_b.attach(product_b)

    assert user_a.child().username == "jane"
    assert user_a.child().username == "jane"

    # Test Many-To-Many relationships using Pivot Table
    assert user_b.cars()[0].make == "VW"
    assert car_1.owners()[0].username == "jane"

    assert bank_acc.holder().username == "john"
    assert user_b.parent().username == "john"
    assert len(user_b.products()) == 2
    assert product_a.owner().username == "jane"

# Test .detach()
def test_detach():
    user_a = User.findOrFail(1)
    bank_acc = Bank_Account.findOrFail(2)
    user_a.detach(bank_acc)

    assert user_a.bank_account() == None

def test_detach_pivot():
    user_b = User.findOrFail(2)
    car = Car.findOrFail(1)

    assert len(user_b.cars()) == 1
    
    user_b.detach(car)
    assert len(user_b.cars()) == 0

# Test .save()
def test_save():
    user_a = User.findOrFail(1)
    user_a.password = 'xyz'
    user_a.save()

    user_temp = User.findOrFail(1)

    assert user_temp.password == 'xyz'
