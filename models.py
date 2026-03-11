class Book:
    def __init__(self, ad, yazar, sayfa_sayisi, yil):
        self._ad = ad
        self._yazar = yazar
        self._sayfa_sayisi = sayfa_sayisi
        self._yil = yil
        self._durum = "Müsait"

    def get_ad(self):
        return self._ad

    def set_durum(self, yeni_durum):
        self._durum = yeni_durum
        return f"'{self._ad}' durumu: {yeni_durum}."

    def to_dict(self):
        return {
            "ad": self._ad,
            "yazar": self._yazar,
            "sayfa_sayisi": self._sayfa_sayisi,
            "yil": self._yil,
            "durum": self._durum
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(data["ad"], data["yazar"], data["sayfa_sayisi"], data["yil"])
        book._durum = data.get("durum", "Müsait")
        return book

    def __str__(self):
        return f"Kitap Adı: {self._ad:<20} | Yazar: {self._yazar:<15} | Durum: {self._durum}"

    def display_info(self):
        return f"({self._yil}) {self._ad} - Sayfa: {self._sayfa_sayisi}"


class Person:
    def __init__(self, ad, soyad):
        self._ad = ad
        self._soyad = soyad
        self._kitaplar = []

    def display_info(self):
        return f"Kişi: {self._ad} {self._soyad}"

    def odunc_al(self, kitap_adi):
        self._kitaplar.append(kitap_adi)
        
    def to_dict(self):
        return {
            "type": "Person",
            "ad": self._ad,
            "soyad": self._soyad,
            "kitaplar": self._kitaplar
        }

    @classmethod
    def from_dict(cls, data):
        person = cls(data["ad"], data["soyad"])
        person._kitaplar = data.get("kitaplar", [])
        return person


class User(Person):
    def __init__(self, ad, soyad, ogrenci_no):
        super().__init__(ad, soyad)
        self._ogrenci_no = ogrenci_no

    def display_info(self):
        return f"Öğrenci: {self._ad} {self._soyad} (No: {self._ogrenci_no})"

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "User",
            "ogrenci_no": self._ogrenci_no
        })
        return data

    @classmethod
    def from_dict(cls, data):
        user = cls(data["ad"], data["soyad"], data["ogrenci_no"])
        user._kitaplar = data.get("kitaplar", [])
        return user


class Admin(Person):
    def __init__(self, ad, soyad, yetki_seviyesi):
        super().__init__(ad, soyad)
        self._yetki = yetki_seviyesi
        self._gorev = "Kütüphane Görevlisi"

    def display_info(self):
        return f"Admin: {self._ad} {self._soyad} | Yetki: {self._yetki}"

    def kitap_ekle_yetkisi(self):
        return "Admin yetkisi ile yeni kitap eklenebilir."

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "Admin",
            "yetki_seviyesi": self._yetki
        })
        return data

    @classmethod
    def from_dict(cls, data):
        admin = cls(data["ad"], data["soyad"], data["yetki_seviyesi"])
        admin._kitaplar = data.get("kitaplar", [])
        return admin

import json
import os

class Library:
    def __init__(self):
        self.envanter = []
        self.kullanicilar = {}
        self.toplam_kitap = 0
        self.data_file = "library_data.json"
        self.load_data()

    def save_data(self):
        data = {
            "envanter": [kitap.to_dict() for kitap in self.envanter],
            "toplam_kitap": self.toplam_kitap
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.envanter = [Book.from_dict(b) for b in data.get("envanter", [])]
                self.toplam_kitap = data.get("toplam_kitap", 0)

    def kitap_ekle(self, book_object):
        if isinstance(book_object, Book):
            self.envanter.append(book_object)
            self.toplam_kitap += 1
            self.save_data()
            return f"'{book_object.get_ad()}' kütüphaneye eklendi."
        else:
            raise ValueError("Sadece Kitap tipinde nesneler eklenebilir.")

    def kitap_sil(self, kitap_adi):
        for kitap in self.envanter:
            if kitap.get_ad().lower() == kitap_adi.lower():
                self.envanter.remove(kitap)
                self.toplam_kitap -= 1
                self.save_data()
                return f"'{kitap.get_ad()}' silindi."

        raise ValueError(f"'{kitap_adi}' adında bir kitap bulunamadı.")

    def listele(self):
        # UI'da göstermek için direkt envanter listesini döndürüyoruz
        return self.envanter

    def odunc_kitap_ver(self, kitap_adi, kullanici_nesnesi):
        if not isinstance(kullanici_nesnesi, Person):
            raise ValueError("Geçerli bir kullanıcı nesnesi gerekli.")

        for kitap in self.envanter:
            if kitap.get_ad().lower() == kitap_adi.lower():
                if kitap._durum == "Müsait":
                    kitap.set_durum("Ödünçte")
                    kullanici_nesnesi.odunc_al(kitap_adi)
                    self.save_data()
                    return f"'{kitap.get_ad()}' {kullanici_nesnesi._ad} kişisine ödünç verildi."
                else:
                    raise ValueError(f"'{kitap.get_ad()}' zaten ödünçte.")
        raise ValueError(f"'{kitap_adi}' adında bir kitap bulunamadı.")

    def odunc_kitap_geri_al(self, kitap_adi, kullanici_nesnesi=None):
        for kitap in self.envanter:
            if kitap.get_ad().lower() == kitap_adi.lower():
                if kitap._durum == "Ödünçte":
                    kitap.set_durum("Müsait")
                    if kullanici_nesnesi and kitap_adi in kullanici_nesnesi._kitaplar:
                        kullanici_nesnesi._kitaplar.remove(kitap_adi)
                    self.save_data()
                    return f"'{kitap.get_ad()}' iade edildi."
                else:
                    raise ValueError(f"'{kitap.get_ad()}' zaten kütüphanede.")
        raise ValueError(f"'{kitap_adi}' adında bir kitap bulunamadı.")
