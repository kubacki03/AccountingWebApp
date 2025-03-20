from flask import Flask, render_template, request, redirect, url_for, flash
import datetime as dt
from itertools import zip_longest

app = Flask(__name__)
app.secret_key = 'supersecretkey'

class ListaOperacji:
    def __init__(self):
        self.lista = []

    def dodaj(self,operacja):
        self.lista.append(operacja)

    def czyWolnyNumer(self, numer):
        return all(numer != operacja.id for operacja in self.lista)


def sumaStaPoczAkt():
    return sum(operacja.wartosc for konto in lista_kont.lista if konto.typKonta == "aktywne" for operacja in konto.operacjeDebetowe if operacja.dokument == "Stan początkowy")

def sumaStaPoczPas():
    return sum(operacja.wartosc for konto in lista_kont.lista if konto.typKonta == "pasywne" for operacja in konto.operacjeKredytowe if operacja.dokument == "Stan początkowy")

class Operacja:


    def __init__(self, data, wartosc, dokument,numer):
        self.data = data
        self.wartosc = wartosc
        self.dokument = dokument
        self.id = numer


class Saldo:
    def __init__(self, typ, wartosc):
        self.typ = typ
        self.wartosc = wartosc


class Konto:
    def __init__(self, nazwa, typ,numer):
        self.nazwa = nazwa
        self.typKonta = typ
        self.operacjeKredytowe = []
        self.operacjeDebetowe = []
        self.id=numer



    def dodajOperacjeKredytowa(self, operacja):
        self.operacjeKredytowe.append(operacja)

    def dodajOperacjeDebetowa(self, operacja):
        self.operacjeDebetowe.append(operacja)

    def wyliczObrotyDebetowe(self):
        return sum(operacja.wartosc for operacja in self.operacjeDebetowe)

    def wyliczObrotyKredytowe(self):
        return sum(operacja.wartosc for operacja in self.operacjeKredytowe)

    def wyliczObrotyKredytoweData(self, data_graniczna):
        return sum(operacja.wartosc for operacja in self.operacjeKredytowe if operacja.data < data_graniczna)

    def wyliczObrotyDebetoweData(self, data_graniczna):
        return sum(operacja.wartosc for operacja in self.operacjeDebetowe if operacja.data < data_graniczna)

    def wyliczSaldo(self, data_graniczna=None):
        if data_graniczna:
            obroty_kredytowe = self.wyliczObrotyKredytoweData(data_graniczna)
            obroty_debetowe = self.wyliczObrotyDebetoweData(data_graniczna)
        else:
            obroty_kredytowe = self.wyliczObrotyKredytowe()
            obroty_debetowe = self.wyliczObrotyDebetowe()

        if obroty_debetowe > obroty_kredytowe:
            return Saldo("debetowe", obroty_debetowe - obroty_kredytowe)
        elif obroty_debetowe < obroty_kredytowe:
            return Saldo("kredytowe", obroty_kredytowe - obroty_debetowe)
        else:
            return Saldo("Zerowe",0)


class ListaKont:
    def __init__(self):
        self.lista = []

    def dodajKonto(self, konto):
        self.lista.append(konto)

    def sumaAktyw(self, data_graniczna=None):
        return sum(konto.wyliczSaldo(data_graniczna).wartosc for konto in self.lista if konto.typKonta == "aktywne")

    def sumaPasyw(self, data_graniczna=None):
        return sum(konto.wyliczSaldo(data_graniczna).wartosc for konto in self.lista if konto.typKonta == "pasywne")

    def podsumowanie(self):
        aktywa = []
        pasywa = []

        for konto in self.lista:
            saldo = konto.wyliczSaldo()
            if konto.typKonta == "aktywne":
                aktywa.append((konto.nazwa, saldo.wartosc))
            elif konto.typKonta == "pasywne":
                pasywa.append((konto.nazwa, saldo.wartosc))

        return {
            "aktywa": aktywa,
            "pasywa": pasywa,
            "suma_aktywa": self.sumaAktyw(),
            "suma_pasywa": self.sumaPasyw()
        }

    def podsumowanieData(self, data_graniczna):
        aktywa = []
        pasywa = []

        for konto in self.lista:
            saldo = konto.wyliczSaldo(data_graniczna)
            if konto.typKonta == "aktywne":
                aktywa.append((konto.nazwa, saldo.wartosc))
            elif konto.typKonta == "pasywne":
                pasywa.append((konto.nazwa, saldo.wartosc))

        return {
            "aktywa": aktywa,
            "pasywa": pasywa,
            "suma_aktywa": self.sumaAktyw(data_graniczna),
            "suma_pasywa": self.sumaPasyw(data_graniczna)
        }

    def getKontoByName(self, nazwa):
        for konto in self.lista:
            if konto.nazwa == nazwa:
                return konto
        return None

    def operacjeNaKoncie(self, nazwa):
        konto = self.getKontoByName(nazwa)
        if konto:
            return {
                "kredytowe": konto.operacjeKredytowe,
                "debetowe": konto.operacjeDebetowe
            }
        else:
            return None


Srodki_w_kasie = Konto("Srodki w kasie", "aktywne",140)
Kapital_podstawowy = Konto("Kapital podstawowy", "pasywne",80)
Srodki_transportu=Konto("Srodki transportu","aktywne",310)
Urzadzenie_techniczne_i_maszyny =Konto("Urzadzenie techniczne i maszyny","aktywne",320)
Umorzenie_urzadzen_technicznych_i_maszyn =Konto("Umorzenie urzadzen technicznych i maszyn","pasywne" ,520)
Naleznosci_z_tytulu_dostaw_i_uslug_do_12_msc =Konto("Naleznosci z tytulu dostaw i uslug do 12 msc","aktywne",290)
Srodki_na_rachunkach_bankowych= Konto("Srodki na rachunkach bankowych","aktywne",150)
ZyskStrata_neto=Konto("Zysk Strata netto","pasywne",450)
Zobowiazania=Konto("Zobowiazania z tytutlu dostaw i uslug do 12 msc","pasywne",240)
Kredyty_bankowe=Konto("Kredyty bankowe krotkoterminowe","pasywne",607)
Zobowiazania_wynagrodzenia=Konto("Zobowiazania z tytulu wynagrodzen","pasywne",230)
Zobowiazania_publicznoprawne=Konto("Zobowiazania z tytulow publicznoprawnych","pasywne",220)
Towary= Konto("Towary","aktywne",330)
Nieruchomosci=Konto("Nieruchomości","aktywne",340)

lista_kont = ListaKont()

lista_kont.dodajKonto(Kapital_podstawowy)

lista_kont.dodajKonto(Srodki_w_kasie)
lista_kont.dodajKonto(Srodki_na_rachunkach_bankowych)

lista_kont.dodajKonto(Zobowiazania_publicznoprawne)
lista_kont.dodajKonto(Zobowiazania_wynagrodzenia)
lista_kont.dodajKonto(Zobowiazania)
lista_kont.dodajKonto(Naleznosci_z_tytulu_dostaw_i_uslug_do_12_msc)


lista_kont.dodajKonto(Srodki_transportu)
lista_kont.dodajKonto(Urzadzenie_techniczne_i_maszyny)
lista_kont.dodajKonto(Towary)
lista_kont.dodajKonto(Nieruchomosci)

lista_kont.dodajKonto(ZyskStrata_neto)

lista_kont.dodajKonto(Umorzenie_urzadzen_technicznych_i_maszyn)







lista_kont.dodajKonto(Kredyty_bankowe)




lista_operacji=ListaOperacji()

@app.route('/')
def index():
    return render_template('index.html', konta=lista_kont.lista)


@app.route('/dodaj-operacje', methods=['POST'])
def dodaj_operacje():
    suma_stanu_poczatkowego_akt = sumaStaPoczAkt()
    suma_stanu_poczatkowego_pas = sumaStaPoczPas()
    if suma_stanu_poczatkowego_akt != suma_stanu_poczatkowego_pas:
        flash("Suma stanów początkowych kont aktywnych nie równa się sumie stanów początkowych kont pasywnych.",
              "error")
        return redirect(url_for('index'))



    numer =request.form['numerOperacji']

    data = request.form['data']
    wartosc = float(request.form['wartosc'])
    dokument = request.form['dokument']

    konto1_name = request.form['konto1']
    konto1_type = request.form['konto1_type']
    konto2_name = request.form['konto2']
    konto2_type = request.form['konto2_type']



    if konto1_name == konto2_name:
        flash("Konta musza byc rozne !!!", "error")
        return redirect(url_for('index'))

    if not lista_operacji.czyWolnyNumer(numer):
        flash("Operacja o takim numerze wystapila","error")
        return redirect(url_for('index'))


    operacja = Operacja(dt.datetime.strptime(data, "%Y-%m-%d").date(), wartosc, dokument,numer)

    konto1 = lista_kont.getKontoByName(konto1_name)
    konto2 = lista_kont.getKontoByName(konto2_name)

    if konto1:
        if konto1_type == "kredytowa":
            konto1.dodajOperacjeKredytowa(operacja)
        elif konto1_type == "debetowa":
            konto1.dodajOperacjeDebetowa(operacja)

    if konto2:
        if konto2_type == "kredytowa":
            konto2.dodajOperacjeKredytowa(operacja)
        elif konto2_type == "debetowa":
            konto2.dodajOperacjeDebetowa(operacja)

    lista_operacji.dodaj(operacja)
    return redirect(url_for('index'))


@app.route('/reset', methods=['POST'])
def reset():
    global lista_kont
    # Reset each account
    for konto in lista_kont.lista:
        konto.operacjeKredytowe = []
        konto.operacjeDebetowe = []
    # Optionally, reset any other state or data as required
    lista_operacji.lista=[]
    return redirect(url_for('index'))

@app.route('/ustaw-stan-poczatkowy', methods=['POST'])
def ustaw_stan_poczatkowy():
    konto_name = request.form['konto']
    stan_poczatkowy = float(request.form['stan_poczatkowy'])
    dataSt = request.args.get('dataStanu')
    konto = lista_kont.getKontoByName(konto_name)
    numer=-1
    if konto:
        if dataSt:
            operacja = Operacja(dataSt, stan_poczatkowy, "Stan początkowy",numer)
            if konto.typKonta == "aktywne":
                konto.dodajOperacjeDebetowa(operacja)
            elif konto.typKonta == "pasywne":
                konto.dodajOperacjeKredytowa(operacja)
        else:
            operacja = Operacja(dt.date.today(), stan_poczatkowy, "Stan początkowy",numer)
            if konto.typKonta == "aktywne":
                konto.dodajOperacjeDebetowa(operacja)
            elif konto.typKonta == "pasywne":
                konto.dodajOperacjeKredytowa(operacja)

    return redirect(url_for('index'))  # Przekierowanie z powrotem do strony głównej


@app.route('/bilans')
def bilans():
    suma_stanu_poczatkowego_akt = sumaStaPoczAkt()
    suma_stanu_poczatkowego_pas = sumaStaPoczPas()
    roznica = abs(suma_stanu_poczatkowego_pas - suma_stanu_poczatkowego_akt)
    if suma_stanu_poczatkowego_akt != suma_stanu_poczatkowego_pas:
        if suma_stanu_poczatkowego_akt > suma_stanu_poczatkowego_pas:
            coWieksze = "aktywa"
        else:
            coWieksze = "pasywne"
        flash(
            f"Suma stanów początkowych kont aktywnych nie równa się sumie stanów początkowych kont pasywnych. Konta '{coWieksze}' są większe o '{roznica}'",
            "error")
        return redirect(url_for('index'))

    errors = []
    for konto in lista_kont.lista:
        saldo = konto.wyliczSaldo()
        if konto.typKonta == "aktywne" and saldo.typ == "kredytowe":
            errors.append(f"Konto aktywne '{konto.nazwa}' ma saldo kredytowe: {saldo.wartosc}")
        elif konto.typKonta == "pasywne" and saldo.typ == "debetowe":
            errors.append(f"Konto pasywne '{konto.nazwa}' ma saldo debetowe: {saldo.wartosc}")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for('index'))

    data_graniczna_str = request.args.get('data_graniczna')

    if data_graniczna_str:
        data_graniczna = dt.datetime.strptime(data_graniczna_str, "%Y-%m-%d").date() + dt.timedelta(days=1)
        podsumowanie = lista_kont.podsumowanieData(data_graniczna)
    else:
        podsumowanie = lista_kont.podsumowanie()

    zipped_aktywa_pasywa = list(zip_longest(podsumowanie['aktywa'], podsumowanie['pasywa'], fillvalue=('', 0)))

    return render_template('bilans.html', podsumowanie=podsumowanie, data_graniczna=data_graniczna_str,
                           zipped_aktywa_pasywa=zipped_aktywa_pasywa)


@app.route('/operacje/<string:konto_nazwa>')
def operacje(konto_nazwa):
    operacje = lista_kont.operacjeNaKoncie(konto_nazwa)
    konto = lista_kont.getKontoByName(konto_nazwa)
    return render_template('operacje.html', operacje=operacje, konto=konto)

def wszystkie():
    lista= lista_operacji
    return  render_template('wszystkie.html',operacje=lista)

if __name__ == '__main__':
    app.run(debug=True)
