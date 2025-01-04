import unittest
from project import db, app
from project.books.models import Book


class TestBookModel(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Testy poprawnych operacji

    def test_add_book(self):
        book = Book('Lalka', 'Boleslaw Prus', 1890, 'proza')
        db.session.add(book)
        db.session.commit()
        self.assertTrue(book.id)

    def test_add_multiple_books(self):
        book1 = Book('Pan Tadeusz', 'Adam Mickiewicz', 1834, 'epopeja')
        book2 = Book('Ogniem i Mieczem', 'Henryk Sienkiewicz', 1884, 'proza')
        db.session.add(book1)
        db.session.commit()
        db.session.add(book2)
        db.session.commit()
        self.assertTrue(book1.id)
        self.assertTrue(book2.id)

    def test_delete_book(self):
        book = Book('Chlopi', 'Wladyslaw Reymont', 1904, 'proza')
        db.session.add(book)
        db.session.commit()
        db.session.delete(book)
        db.session.commit()
        self.assertIsNone(Book.query.get(book.id))

    def test_get_book_by_name(self):
        book = Book('Dziady', 'Adam Mickiewicz', 1823, 'dramat')
        db.session.add(book)
        db.session.commit()
        book = Book.query.filter_by(name='Dziady').first()
        self.assertTrue(book)

    def test_update_book(self):
        book = Book('Hobbit', 'J.R.R. Tolkien', 1937, 'proza')
        db.session.add(book)
        db.session.commit()
        book_to_update = Book.query.get(book.id)
        book_to_update.name = 'Hobbit, czyli tam i z powrotem'
        db.session.commit()
        self.assertEqual(book.name, 'Hobbit, czyli tam i z powrotem')

    def test_get_all_books(self):
        book1 = Book('W pustyni i w puszczy', 'Henryk Sienkiewicz', 1911, 'proza')
        book2 = Book('Dzieci z Bullerbyn', 'Astrid Lindgren', 1947, 'dla dzieci')
        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()
        books = Book.query.all()
        self.assertEqual(len(books), 2)

    # Testy niepoprawnych operacji

    def test_add_book_empty_title(self):
        book = Book('', 'Autor', 2000, 'proza')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_empty_author(self):
        book = Book('Tytul', '', 2000, 'proza')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_invalid_year_published(self):
        book = Book('Tytul', 'Autor', 'rok2000', 'proza')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_invalid_book_type(self):
        book = Book('Tytul', 'Autor', 2000, None)
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_duplicate_title(self):
        book1 = Book('Tytul', 'Autor', 2000, 'proza')
        book2 = Book('Tytul', 'Autor', 2000, 'proza')
        db.session.add(book1)
        db.session.add(book2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_delete_book_not_exists(self):
        book = Book('Tytul', 'Autor', 2000, 'proza')
        db.session.add(book)
        db.session.commit()
        db.session.delete(book)
        db.session.commit()
        with self.assertRaises(Exception):
            db.session.delete(book)
            db.session.commit()

    # Testy związane z próbą wstrzyknięcia kodu SQL i JavaScript

    def test_add_book_sql_injection(self):
        book = Book('Tytul', 'Autor\'); DROP TABLE books; --', 1900, 'dramat')
        db.session.add(book)
        db.session.commit()
        self.assertTrue(book.id)
        self.assertNotIn('DROP TABLE books', book.author)

    def test_update_book_sql_injection(self):
        book = Book('Tytul', 'Autor', 1900, 'dramat')
        db.session.add(book)
        db.session.commit()
        book.title = '\'); DROP TABLE books; --'
        db.session.commit()
        self.assertNotIn('DROP TABLE books', book.title)

    def test_add_book_js_injection(self):
        book = Book('Tytul', 'Autor<script>alert("XSS");</script>', 1900, 'dramat')
        db.session.add(book)
        db.session.commit()
        self.assertTrue(book.id)
        self.assertNotIn('<script>', book.author)

    def test_update_book_js_injection(self):
        book = Book('Tytul', 'Autor', 1900, 'dramat')
        db.session.add(book)
        db.session.commit()
        book.title = '<script>alert(document.cookie);</script>'
        db.session.commit()
        self.assertNotIn('<script>', book.title)

    # Testy ekstremalne 

    def test_add_book_long_title(self):
        book = Book('A' * 65, 'Autor', 1950, 'literatura piekna')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_long_author(self):
        book = Book('Tytul', 'B' * 65, 1950, 'literatura piekna')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()
        
    def test_add_book_big_year_published(self):
        book = Book('Tytul', 'Autor', 1000000, 'literatura piekna')
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_add_book_long_book_type(self):
        book = Book('Tytul', 'Autor', 2000, 'D' * 21)
        db.session.add(book)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
