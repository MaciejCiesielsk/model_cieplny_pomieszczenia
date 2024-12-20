# model_cieplny_pomieszczenia

zeby dzialalo trzeba pobrac dasha - moze byc wymagany venv do tego

* czas probkowania  DODANY
* symulacja po przycisku simulate, bo stare wykresy maja zostawac DODANY
* kp ti td ma byc suwakiem RACZEJ ZOSTAWIE JAK JEST
* przycisk reset do usuwania starych wykresow  JEST DZIALA
* czas symulacji hardcoded  DZIALA

# Dlaczego takie duze wartosci parametrow?
* dostosowane do specyficznych wlasnosci systemu - duza pojemnosc pomieszczenia i moc grzewcza
* zeby system byl stabilny trzeba bylo duze parametry
* moze byc ten kompensacja strat - np slaba izolacja i trzeba nadrobic uciekanie ciepla 
* dostosowanie do warunkow zewnetrznych


# Dlaczego uklad jest inercyjny?
Zawiera charakterysyczne dla ukladu inercyjnego parametry:
* pojemnosc cieplna - pomieszczenie ma okreslona gestosc powietrza i pojemnosc cieplna, co powoduje stopniowa zmiane temp a nie instant
* utrata ciepla - zalezy od temperatury na dwore i to powoduje opoznienie w dzialaniu

# Poszczegolne czlony regulatora
* P - odpowiada bezposrednio na biezacy blad, im wiekszy blad tym wieksza odpowiedz regulatora (intensywnosc odpowiedzi na blad)
* I - odpowiaa na sume bledow w czasie, dziala wolniej ale zapewnia dokladnosc w dluzszym okresie (sumuje bledy)
* D - odpowiada na szybkosc zmiany bledu, co pozwala dzilac szybciej i przewidziec pryszle bledy (opoznia i uspokaja)

# Co to jest za wspolczynnik izolacji
od stycznia 2021 roku nie może przekraczać 0,20 W/(m²·K) - waty na metr kwadratowy razy kelwin (wspolczynnik przenikania ciepla U)