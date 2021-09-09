from io import BytesIO
from typing import NoReturn

from django.test import TestCase

from .views import process_category_upload, process_menu_upload
from restaurant.models import Category, Menu, Restaurant


class CategoryImportTests(TestCase):
    restaurant: Restaurant  # needed to help VSCode type inference

    @classmethod
    def setUpTestData(cls) -> NoReturn:
        cls.restaurant: Restaurant = Restaurant.objects.create(
            name="Test Restaurant"
        )

    def test_fresh_import(self) -> NoReturn:
        """
        Imports two categories, both with descriptions set. This should succeed and return `2`.
        """
        f: BytesIO = BytesIO('''Name,Description
Test 1,First test category
Test 2,Second test category'''.encode('utf-8'))
        count: int = process_category_upload(f, self.restaurant)
        self.assertEqual(count, 2)
        self.assertEqual(Category.objects.filter(cat_name="test 1", description="First test category").count(), 1)
        self.assertEqual(Category.objects.filter(cat_name="test 2", description="Second test category").count(), 1)

    def test_fresh_import_missing_desc(self) -> NoReturn:
        """
        Imports a category without a description set. It should import successfully with its description set to
        an empty string.
        """
        f: BytesIO = BytesIO('''Name,Description
Test,'''.encode('utf-8'))
        count: int = process_category_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.filter(cat_name="test", description="").count(), 1)

    def test_snapshot_add_new(self) -> NoReturn:
        """
        Imports a new category from a snapshot without interfering with the old one.
        """
        Category.objects.create(
            cat_name="Category 1",
            description="First test category",
            restaurant=self.restaurant,
        )

        f: BytesIO = BytesIO('''Name,Description
Category 2,Second test category'''.encode('utf-8'))
        count: int = process_category_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Category.objects.filter(cat_name="category 1", description="First test category").count(), 1)
        self.assertEqual(Category.objects.filter(cat_name="category 2", description="Second test category").count(), 1)

    def test_snapshot_update_existing(self) -> NoReturn:
        """
        Updates an existing category from a snapshot correctly.
        """
        Category.objects.create(
            cat_name="Category",
            description="One",
            restaurant=self.restaurant,
        )

        f: BytesIO = BytesIO('''Name,Description
Category,Two'''.encode('utf-8'))
        count: int = process_category_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.filter(cat_name="category", description="Two").count(), 1)


class MenuImportTests(TestCase):
    restaurant: Restaurant  # needed to help VSCode type inference

    @classmethod
    def setUpTestData(cls) -> NoReturn:
        cls.restaurant: Restaurant = Restaurant.objects.create(
            name="Test Restaurant"
        )

    def test_fresh_import(self) -> NoReturn:
        """
        Imports two menus with all attributes set, using unique non-existent categories. This should succeed and return `2`.
        """
        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category 1,Test 1,9.99,First test item,https://example.com/image1.jpg
Category 2,Test 2,17.98,Second test item,https://example.com/image2.jpg'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 2)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Menu.objects.filter(
            title="Test 1",
            price=9.99,
            description="First test item",
            image_url="https://example.com/image1.jpg",
        ).count(), 1)
        self.assertEqual(Menu.objects.filter(
            title="Test 2",
            price=17.98,
            description="Second test item",
            image_url="https://example.com/image2.jpg",
        ).count(), 1)

    def test_fresh_import_missing_attributes(self) -> NoReturn:
        """
        Imports a menu with the minimum possible attributes (category, name, price). This should succeed and have
        the other attributes defaulted as expected.
        """
        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category,Test,9.99,,'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Menu.objects.filter(description="", image_url="").count(), 1)

    def test_fresh_import_shared_category(self) -> NoReturn:
        """
        Imports two menus with the same, non-existent category. This should succeed and result in the creation
        of only one new category.
        """
        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category,Test 1,9.99,First test item,https://example.com/image1.jpg
Category,Test 2,17.98,Second test item,https://example.com/image2.jpg'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 2)
        self.assertEqual(Category.objects.count(), 1)

    def test_fresh_import_reuse_category(self) -> NoReturn:
        """
        Imports a menu using an existing category. This should succeed and not create a new category.
        """
        old_category: Category = Category.objects.create(
            cat_name="Category",
            restaurant=self.restaurant,
        )

        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category,Test,9.99,Test item,https://example.com/image.jpg'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Menu.objects.first().category, old_category)

    def test_snapshot_add_new(self) -> NoReturn:
        """
        Imports a new menu from a snapshot without interfering with the old one.
        """
        old_category: Category = Category.objects.create(
            cat_name="Category 1",
            restaurant=self.restaurant,
        )
        old_menu: Menu = Menu.objects.create(
            owner=self.restaurant,
            user=self.restaurant.owner,
            category=old_category,
            title="Test 1",
            price=0.99,
            description="Old test item",
            image_url="https://example.com/image1.jpg"
        )

        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category 2,Test 2,1.99,New test item,https://example.com/image2.jpg'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Menu.objects.count(), 2)
        self.assertEqual(Menu.objects.filter(
            title="Test 1",
            price=0.99,
            description="Old test item",
            image_url="https://example.com/image1.jpg"
        ).count(), 1)
        self.assertEqual(Menu.objects.filter(
            title="Test 2",
            price=1.99,
            description="New test item",
            image_url="https://example.com/image2.jpg"
        ).count(), 1)

    def test_snapshot_update_existing(self) -> NoReturn:
        """
        Updates an existing menu from a snapshot correctly.
        """
        category: Category = Category.objects.create(
            cat_name="Category",
            restaurant=self.restaurant,
        )
        Menu.objects.create(
            owner=self.restaurant,
            user=self.restaurant.owner,
            category=category,
            title="Test",
            price=0.99,
            description="One",
            image_url="https://example.com/image1.jpg"
        )

        f: BytesIO = BytesIO('''Category,Menu Item,Price,Description,Image URL
Category,Test,1.99,Two,https://example.com/image2.jpg'''.encode('utf-8'))
        count: int = process_menu_upload(f, self.restaurant)
        self.assertEqual(count, 1)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(Menu.objects.filter(
            title="Test",
            price=1.99,
            description="Two",
            image_url="https://example.com/image2.jpg"
        ).count(), 1)
