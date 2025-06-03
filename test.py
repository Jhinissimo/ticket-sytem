import json
from datetime import datetime


class MiejsceTeatralne:
    def __init__(self, numer, cena):
        self.numer = numer
        self.cena = cena
        self.dostepnosc = True
        self.klient = None

    def zarezerwuj(self, klient):
        if self.dostepnosc:
            self.dostepnosc = False
            self.klient = klient
            return True
        return False

    def anuluj_rezerwacje(self, klient):
        if not self.dostepnosc and self.klient == klient:
            self.dostepnosc = True
            self.klient = None
            return True
        return False

    def __str__(self):
        return f"Miejsce {self.numer} ({self.__class__.__name__}): Cena: {self.cena:.2f} zł"


class MiejsceZwykle(MiejsceTeatralne):
    def __init__(self, numer, cena):
        super().__init__(numer, cena)


class MiejsceVIP(MiejsceTeatralne):
    def __init__(self, numer, cena, dodatkowe_udogodnienia):
        super().__init__(numer, cena * 1.2)
        self.dodatkowe_udogodnienia = dodatkowe_udogodnienia

    def __str__(self):
        return f"{super().__str__()}, Udogodnienia: {', '.join(self.dodatkowe_udogodnienia)}"


class MiejsceDlaNiepelnosprawnych(MiejsceTeatralne):
    def __init__(self, numer, cena, przystosowanie):
        super().__init__(numer, cena * 0.8)
        self.przystosowanie = przystosowanie

    def __str__(self):
        return f"{super().__str__()}, Przystosowanie: {self.przystosowanie}"


class Klient:
    _next_id = 1

    def __init__(self, imie, nazwisko):
        self.id_klienta = Klient._next_id
        Klient._next_id += 1
        self.imie = imie
        self.nazwisko = nazwisko
        self.historia_rezerwacji = []

    def dodaj_rezerwacje(self, miejsce):
        self.historia_rezerwacji.append({
            'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'miejsce': miejsce,
            'status': 'aktywna'
        })

    def anuluj_rezerwacje(self, miejsce):
        for rezerwacja in self.historia_rezerwacji:
            if rezerwacja['miejsce'] == miejsce and rezerwacja['status'] == 'aktywna':
                rezerwacja['status'] = 'anulowana'
                rezerwacja['data_anulowania'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
        return False

    def pokaz_historie(self):
        print(f"\nHistoria rezerwacji dla {self.imie} {self.nazwisko}:")
        for idx, rezerwacja in enumerate(self.historia_rezerwacji, 1):
            status = rezerwacja['status']
            miejsce = rezerwacja['miejsce']
            data = rezerwacja['data']
            print(f"{idx}. {data} | {miejsce} | Status: {status}")

    def eksportuj_historie(self, filename=None):
        if not filename:
            filename = f"rezerwacje_{self.id_klienta}_{datetime.now().strftime('%Y%m%d%H%M')}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Historia rezerwacji klienta {self.id_klienta}\n")
            f.write(f"Imię i nazwisko: {self.imie} {self.nazwisko}\n")
            f.write("============================================\n")
            for rezerwacja in self.historia_rezerwacji:
                f.write(f"{rezerwacja['data']} | {rezerwacja['miejsce']} | Status: {rezerwacja['status']}\n")
        print(f"Historia została wyeksportowana do pliku {filename}")


class Teatr:
    def __init__(self):
        self.miejsca = []
        self.klienci = []
        self._init_miejsca()

    def _init_miejsca(self):
        for i in range(1, 31):
            self.miejsca.append(MiejsceZwykle(i, 50))

        for i in range(31, 41):
            self.miejsca.append(MiejsceVIP(i, 100, ["loża", "kelner"]))

        for i in range(41, 51):
            self.miejsca.append(MiejsceDlaNiepelnosprawnych(i, 50, "podjazd dla wózków"))

    def znajdz_miejsce(self, numer_miejsca):
        for miejsce in self.miejsca:
            if miejsce.numer == numer_miejsca:
                return miejsce
        return None

    def znajdz_klienta(self, id_klienta):
        for klient in self.klienci:
            if klient.id_klienta == id_klienta:
                return klient
        return None

    def rejestruj_klienta(self, imie, nazwisko):
        nowy_klient = Klient(imie, nazwisko)
        self.klienci.append(nowy_klient)
        return nowy_klient

    def rezerwuj_miejsce(self, numer_miejsca, klient):
        miejsce = self.znajdz_miejsce(numer_miejsca)
        if not miejsce:
            return False, "Miejsce nie istnieje"
        if miejsce.zarezerwuj(klient):
            klient.dodaj_rezerwacje(miejsce)
            return True, f"Zarezerwowano miejsce {numer_miejsca} za {miejsce.cena:.2f} zł"
        return False, "Miejsce jest już zajęte"

    def anuluj_rezerwacje(self, numer_miejsca, klient):
        miejsce = self.znajdz_miejsce(numer_miejsca)
        if not miejsce:
            return False, "Miejsce nie istnieje"
        if miejsce.anuluj_rezerwacje(klient):
            klient.anuluj_rezerwacje(miejsce)
            return True, "Anulowano rezerwację"
        return False, "Nie możesz anulować tej rezerwacji"

    def pokaz_dostepne_miejsca(self):
        print("\nDostępne miejsca:")
        for miejsce in sorted(self.miejsca, key=lambda m: m.numer):
            if miejsce.dostepnosc:
                print(miejsce)

    def eksportuj_stan_miejsc(self, filename=None):
        if not filename:
            filename = f"stan_miejsc_{datetime.now().strftime('%Y%m%d%H%M')}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Stan miejsc w teatrze\n")
            f.write("============================================\n")
            for miejsce in self.miejsca:
                status = "Dostępne" if miejsce.dostepnosc else f"Zajęte przez klienta {miejsce.klient.id_klienta if miejsce.klient else '?'}"
                f.write(f"{miejsce} | Status: {status}\n")
        print(f"Stan miejsc został wyeksportowany do pliku {filename}")



if __name__ == "__main__":
    teatr = Teatr()

    while True:
        print("\n1. Pokaż dostępne miejsca")
        print("2. Zarejestruj nowego klienta")
        print("3. Zarezerwuj miejsce")
        print("4. Anuluj rezerwację")
        print("5. Pokaż historię rezerwacji")
        print("6. Eksportuj historię rezerwacji klienta")
        print("7. Eksportuj stan miejsc")
        print("8. Wyjdź")
        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            teatr.pokaz_dostepne_miejsca()

        elif wybor == "2":
            imie = input("Podaj imię: ")
            nazwisko = input("Podaj nazwisko: ")
            klient = teatr.rejestruj_klienta(imie, nazwisko)
            print(f"Zarejestrowano klienta o ID {klient.id_klienta}")

        elif wybor == "3":
            numer = int(input("Podaj numer miejsca: "))
            id_klienta = int(input("Podaj ID klienta: "))
            klient = teatr.znajdz_klienta(id_klienta)
            if klient:
                success, msg = teatr.rezerwuj_miejsce(numer, klient)
                print(msg)
            else:
                print("Nie znaleziono klienta o podanym ID")

        elif wybor == "4":
            numer = int(input("Podaj numer miejsca: "))
            id_klienta = int(input("Podaj ID klienta: "))
            klient = teatr.znajdz_klienta(id_klienta)
            if klient:
                success, msg = teatr.anuluj_rezerwacje(numer, klient)
                print(msg)
            else:
                print("Nie znaleziono klienta o podanym ID")

        elif wybor == "5":
            id_klienta = int(input("Podaj ID klienta: "))
            klient = teatr.znajdz_klienta(id_klienta)
            if klient:
                klient.pokaz_historie()
            else:
                print("Nie znaleziono klienta o podanym ID")

        elif wybor == "6":
            id_klienta = int(input("Podaj ID klienta: "))
            klient = teatr.znajdz_klienta(id_klienta)
            if klient:
                klient.eksportuj_historie()
            else:
                print("Nie znaleziono klienta o podanym ID")

        elif wybor == "7":
            teatr.eksportuj_stan_miejsc()

        elif wybor == "8":
            break

        else:
            print("Nieprawidłowy wybór")