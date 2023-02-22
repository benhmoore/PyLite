import os
import unittest
from lite import *

# define a SQLite connection
TEST_DB_PATH = "test.sqlite"


class Pet(LiteModel):

    def owner(self):
        return self.belongsTo(Person)

class Brain(LiteModel):

    def owner(self):
        return self.belongsTo(Person)

class Person(LiteModel):

    TABLE_NAME = "people"

    def pets(self):
        return self.hasMany(Pet)

    def brain(self):
        return self.hasOne(Brain)

    def memberships(self):
        return self.belongsToMany(Membership)

class Membership(LiteModel):
    
        def people(self):
            return self.belongsToMany(Person)

Membership.pivotsWith(Person, 'membership_person')

class TestLiteModel(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """Create a test database"""
        Lite.createDatabase(TEST_DB_PATH)
        Lite.connect(LiteConnection(database_path=TEST_DB_PATH))

        # Create Pet table
        LiteTable.createTable("pets", {
            "name": "TEXT",
            "age": "INTEGER",
            "owner_id": "INTEGER"
        }, {
            "owner_id": ("people", "id")
        })

        # Create Brain table
        LiteTable.createTable("brains", {
            "name": "TEXT",
            "person_id": "INTEGER"
        })

        # Create Person table
        LiteTable.createTable("people", {
            "name": "TEXT",
            "age": "INTEGER",
        })

        # Create Person table
        LiteTable.createTable("memberships", {
            "name": "TEXT",
        })

        LiteTable.createTable('membership_person', {
            'person_id': 'INTEGER',
            'membership_id': 'INTEGER',
        },{
            "person_id":['people','id'],
            "membership_id":['memberships','id']
        })

    @classmethod
    def tearDownClass(self):
        """Delete the test database"""
        os.remove(TEST_DB_PATH)


    def setUp(self):
        """Create a new Person and Pet"""
        self.person = Person.create({
            "name": "John",
            "age": 25
        })
        self.pet = Pet.create({
            "name": "Fido",
            "age": 3,
        })

        self.memberships = Membership.createMany([
            {
                "name": "membership1"
            },
            {
                "name": "membership2"
            },
        ])

    def tearDown(self):
        """Delete the Person and Pet"""
        self.person.delete()
        self.pet.delete()

        self.memberships.deleteAll()

    def test_create(self):
        """Test the create() method"""
        self.assertEqual(self.person.name, "John")
        self.assertEqual(self.person.age, 25)

        self.assertEqual(self.pet.name, "Fido")
        self.assertEqual(self.pet.age, 3)

    def test_belongsToMany(self):
        """Test the belongsToMany() method"""

        # Attach the membership to the person
        self.memberships.attachToAll(self.person)

        # Check that the person's memberships are the membership
        self.assertEqual(self.person.memberships()[0].id, self.memberships[0].id)

    def test_belongsTo(self):
        """Test the belongsTo() method"""

        # Attach the pet to the person
        self.pet.attach(self.person)

        # Check that the pet's owner is the person
        self.assertEqual(self.pet.owner().id, self.person.id)

    def test_hasMany(self):
        """Test the hasMany() method"""

        # Attach the pet to the person
        self.pet.attach(self.person)

        # Check that the person's pets are the pet
        self.assertEqual(self.person.pets()[0].id, self.pet.id)

    def test_hasOne(self):
        """Test the hasOne() method"""

        # Attach the brain to the person
        brain = Brain.create({
            "name": "Brain",
        })
        brain.attach(self.person)

        # Check that the person's brain is the brain
        self.assertEqual(self.person.brain().id, brain.id)

    def test_findOrFail(self):
        """Test the findOrFail() method"""

        # Check that the person can be found
        self.assertEqual(Person.findOrFail(self.person.id).id, self.person.id)

        # Check that an exception is raised if the person can't be found
        with self.assertRaises(ModelInstanceNotFoundError):
            Person.findOrFail(100)

    def test_find(self):
        """Test the find() method"""

        # Check that the person can be found
        self.assertEqual(Person.find(self.person.id).id, self.person.id)

        # Check that None is returned if the person can't be found
        self.assertIsNone(Person.find(100))

    def test_all(self):
        """Test the all() method"""

        person2 = Person.create({
            "name": "Jane",
            "age": 30
        })

        # Check that all people are returned
        self.assertEqual(len(Person.all()), 2)

        person2.delete()
    
    def test_where(self):
        """Test the where() method"""

        person2 = Person.create({
            "name": "Jane",
            "age": 30
        })

        # Check that the correct person is returned
        self.assertEqual(Person.where([
            ["name", "=", "Jane"]            
        ]).first().id, person2.id)

        person2.delete()

    def test_createMany(self):
        """Test the createMany() method"""

        # Create two pets
        new_pets = Pet.createMany([
            {
                "name": "Tulip",
                "age": 3
            },
            {
                "name": "Spot",
                "age": 5
            },
        ])

        # Check that the pets were created
        self.assertEqual(len(Pet.all()), 3)

        # Delete the pets
        new_pets.deleteAll()

        assert len(Pet.all()) == 1

    def test_manyToMany(self):
        """Test the manyToMany() method"""

        # Attach the person to the memberships
        self.person.attachMany(self.memberships)

        # Check that the person's memberships are the memberships
        self.assertEqual(len(self.person.memberships()), 2)

        person2 = Person.create({
            "name": "Jane",
            "age": 30
        })

        # Attach the person to the first membership
        person2.attach(self.memberships[0])

        # Check that the memberships' people are the person
        self.assertEqual(len(self.memberships[0].people()), 2)

        # Detach the person from the first membership
        self.memberships[0].detach(person2)
        self.assertEqual(len(self.memberships[0].people()), 1)

        # Detach the person from the memberships
        self.person.detachMany(self.memberships)
        self.assertEqual(len(self.person.memberships()), 0)

        person2.delete()

    def test_save(self):
        """Test the save() method"""

        # Change the person's name
        self.person.name = "Ben"

        # Save the person
        self.person.save()

        # Check that the person's name was changed
        self.assertEqual(Person.find(self.person.id).name, "Ben")

    def test_fresh(self):
        """Test the fresh() method"""

        # Change the person's name
        self.person.name = "Ben"

        # Check that the person's name hasn't changed
        self.person.fresh()
        self.assertEqual(self.person.name, "John")

    def test_findPath(self):
        """Test the findPath() method"""
        pass