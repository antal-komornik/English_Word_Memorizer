import sqlite3

class szotar_kezelese:

    def __init__(self):
        self.kapcsolat = sqlite3.connect("word_memorizer.db")
        self.helyes = 0
        self.hibas = 0
        self.elozo = None
        self.hibas_szavak = []

    def valasztas(self):
        ab = self.kapcsolat.cursor()

        while True:
            ab.execute("""
                SELECT english, hungarian
                FROM dictionary_random_100
                ORDER BY RANDOM()
                LIMIT 1
            """)

            szo = ab.fetchone()

            if szo != self.elozo:
                self.elozo = szo
                return szo

    def ellenoriz(self, valasz, helyes):
        if valasz.lower().strip() == helyes.lower().strip():
            self.helyes += 1
            return True
        else:
            self.hibas += 1
            self.hibas_szavak.append(helyes)
            return False

    def statisztika(self):
        return self.helyes, self.hibas

    def bezar(self):
        self.kapcsolat.close()