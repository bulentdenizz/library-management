from models import Book, Library

lib = Library()
# setup fake inventory
b1 = Book("sefiller", "victor", 1000, 1888)
lib.kitap_ekle(b1)
lib.kitap_sil("sefiller")
print("Done")
