import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, 
                             QLabel, QLineEdit, QGroupBox, QFormLayout, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

# Import our backend models
from models import Library, Book, User, Admin

class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kütüphane Yönetim Sistemi")
        self.resize(800, 600)
        
        self.library = Library()
        
        # Test users and books to start with (same as your notebook)
        self.test_user = User("Ali", "Yılmaz", "12345")
        self.test_admin = Admin("Ayşe", "Kaya", "Üst Düzey")
        
        # Sadece kütüphane boşsa örnek kitapları ekle
        if self.library.toplam_kitap == 0:
            book1 = Book("Ornek1", "OrnekY1", 100, 1999)
            book2 = Book("Ornek2", "OrnekY2", 150, 1985)
            self.library.kitap_ekle(book1)
            self.library.kitap_ekle(book2)
        
        # Main layout wrapper
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.tab_inventory = QWidget()
        self.tab_operations = QWidget()
        
        self.tabs.addTab(self.tab_inventory, "📚 Kütüphane Envanteri")
        self.tabs.addTab(self.tab_operations, "🛠️ Kitap İşlemleri")
        
        self.init_inventory_tab()
        self.init_operations_tab()
        
        # Initial refresh
        self.refresh_table()
        
    def init_inventory_tab(self):
        layout = QVBoxLayout()
        
        # Table widget setup
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Kitap Adı", "Yazar", "Yıl", "Sayfa Sayısı", "Durum"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read only
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # When user clicks a row, auto-fill the delete/borrow/return text fields
        self.table.itemClicked.connect(self.on_table_click)
        
        layout.addWidget(self.table)
        
        # Refresh button
        self.btn_refresh = QPushButton("Listeyi Yenile")
        self.btn_refresh.setMinimumHeight(40)
        self.btn_refresh.clicked.connect(self.refresh_table)
        layout.addWidget(self.btn_refresh)
        
        self.tab_inventory.setLayout(layout)
        
    def init_operations_tab(self):
        main_layout = QVBoxLayout()
        
        # 1. ADD BOOK
        group_add = QGroupBox("Genel İşlemler: Kitap Ekle")
        form_add = QFormLayout()
        
        self.input_ad = QLineEdit()
        self.input_ad.setPlaceholderText("Örn: Sefiller")
        self.input_yazar = QLineEdit()
        self.input_yazar.setPlaceholderText("Örn: Victor Hugo")
        self.input_yil = QLineEdit()
        self.input_yil.setPlaceholderText("Örn: 1862")
        self.input_sayfa = QLineEdit()
        self.input_sayfa.setPlaceholderText("Örn: 1400")
        
        btn_add = QPushButton("Kütüphaneye Ekle")
        btn_add.setMinimumHeight(35)
        btn_add.clicked.connect(self.add_book)
        
        form_add.addRow("Kitap Adı:", self.input_ad)
        form_add.addRow("Yazar:", self.input_yazar)
        form_add.addRow("Basım Yılı:", self.input_yil)
        form_add.addRow("Sayfa Sayısı:", self.input_sayfa)
        form_add.addRow(btn_add)
        group_add.setLayout(form_add)
        main_layout.addWidget(group_add)
        
        # 2. DELETE BOOK
        group_delete = QGroupBox("Admin İşlemleri: Kitap Sil")
        form_delete = QHBoxLayout()
        self.input_del_ad = QLineEdit()
        self.input_del_ad.setPlaceholderText("Silinecek kitabın adını giriniz")
        btn_del = QPushButton("Kitabı Sil")
        btn_del.setMinimumHeight(35)
        btn_del.clicked.connect(self.delete_book)
        form_delete.addWidget(self.input_del_ad)
        form_delete.addWidget(btn_del)
        group_delete.setLayout(form_delete)
        main_layout.addWidget(group_delete)
        
        # 3. BORROW / RETURN
        group_borrow = QGroupBox(f"Kullanıcı İşlemleri (Mevcut Kullanıcı: {self.test_user._ad} {self.test_user._soyad})")
        form_borrow = QVBoxLayout()
        
        row1 = QHBoxLayout()
        self.input_borrow_ad = QLineEdit()
        self.input_borrow_ad.setPlaceholderText("Ödünç alınacak kitabın adını giriniz")
        btn_borrow = QPushButton("Ödünç Al")
        btn_borrow.setMinimumHeight(35)
        btn_borrow.clicked.connect(self.borrow_book)
        row1.addWidget(self.input_borrow_ad)
        row1.addWidget(btn_borrow)
        
        row2 = QHBoxLayout()
        self.input_return_ad = QLineEdit()
        self.input_return_ad.setPlaceholderText("İade edilecek kitabın adını giriniz")
        btn_return = QPushButton("İade Et")
        btn_return.setMinimumHeight(35)
        btn_return.clicked.connect(self.return_book)
        row2.addWidget(self.input_return_ad)
        row2.addWidget(btn_return)
        
        form_borrow.addLayout(row1)
        form_borrow.addLayout(row2)
        group_borrow.setLayout(form_borrow)
        main_layout.addWidget(group_borrow)
        
        main_layout.addStretch() # Push everything to top
        self.tab_operations.setLayout(main_layout)
        
    def refresh_table(self):
        books = self.library.listele()
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(book.get_ad()))
            self.table.setItem(row, 1, QTableWidgetItem(book._yazar))
            self.table.setItem(row, 2, QTableWidgetItem(str(book._yil)))
            self.table.setItem(row, 3, QTableWidgetItem(str(book._sayfa_sayisi)))
            # Color coding for availability
            durum_item = QTableWidgetItem(book._durum)
            if book._durum == "Müsait":
                durum_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                durum_item.setForeground(Qt.GlobalColor.darkRed)
            self.table.setItem(row, 4, durum_item)
            
    def on_table_click(self, item):
        # Auto-fill selected book name into operation text boxes
        row = item.row()
        book_name = self.table.item(row, 0).text()
        self.input_del_ad.setText(book_name)
        self.input_borrow_ad.setText(book_name)
        self.input_return_ad.setText(book_name)
        
        # Switch to operations tab optionally, or let user decide.
        # self.tabs.setCurrentIndex(1)
            
    def add_book(self):
        ad = self.input_ad.text().strip()
        yazar = self.input_yazar.text().strip()
        yil = self.input_yil.text().strip()
        sayfa = self.input_sayfa.text().strip()
        
        if not ad or not yazar or not yil or not sayfa:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
            return
            
        try:
            yil = int(yil)
            sayfa = int(sayfa)
            new_book = Book(ad, yazar, sayfa, yil)
            msg = self.library.kitap_ekle(new_book)
            QMessageBox.information(self, "Başarılı", msg)
            
            # Clear inputs
            self.input_ad.clear()
            self.input_yazar.clear()
            self.input_yil.clear()
            self.input_sayfa.clear()
            
            self.refresh_table()
        except ValueError as e:
            if "invalid literal" in str(e):
                QMessageBox.critical(self, "Hata", "Sayfa sayısı ve Yıl rakamlardan oluşmalıdır.")
            else:
                QMessageBox.critical(self, "Hata", str(e))
            
    def delete_book(self):
        ad = self.input_del_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir kitap adı girin.")
            return
        
        reply = QMessageBox.question(self, "Emin misiniz?", f"'{ad}' adlı kitabı silmek istediğinize emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                     
        if reply == QMessageBox.StandardButton.Yes:
            try:
                msg = self.library.kitap_sil(ad)
                QMessageBox.information(self, "Başarılı", msg)
                self.input_del_ad.clear()
                self.refresh_table()
            except ValueError as e:
                QMessageBox.warning(self, "Hata", str(e))
            
    def borrow_book(self):
        ad = self.input_borrow_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Uyarı", "Lütfen ödünç alınacak kitabın adını girin.")
            return
            
        try:
            msg = self.library.odunc_kitap_ver(ad, self.test_user)
            QMessageBox.information(self, "Başarılı", msg)
            self.input_borrow_ad.clear()
            self.refresh_table()
        except ValueError as e:
            QMessageBox.warning(self, "Hata", str(e))
            
    def return_book(self):
        ad = self.input_return_ad.text().strip()
        if not ad:
            QMessageBox.warning(self, "Uyarı", "Lütfen iade edilecek kitabın adını girin.")
            return
            
        try:
            msg = self.library.odunc_kitap_geri_al(ad, self.test_user)
            QMessageBox.information(self, "Başarılı", msg)
            self.input_return_ad.clear()
            self.refresh_table()
        except ValueError as e:
            QMessageBox.warning(self, "Hata", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec())
