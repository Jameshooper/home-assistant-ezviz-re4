# EZVIZ RE4 dla Home Assistanta

Polski · [English](README.md)

Nieoficjalna integracja Home Assistanta dla robota **EZVIZ RE4** .
Przetestowana z modelem `CS-RE4C-YWT`.

> Projekt jest eksperymentalny i korzysta z usług chmurowych rozpoznanych w
> aplikacji EZVIZ, ponieważ producent nie publikuje API robota. Zmiana chmury
> lub oprogramowania może czasowo wyłączyć część funkcji.

## Funkcje

- Start, pauza, zatrzymanie i powrót robota do stacji.
- Natywny wybór pomieszczeń i sprzątanie pokoi w Home Assistant.
- Czujniki baterii i zużycia materiałów (szczotka główna, szczotka boczna,
  filtr HEPA, mopy, czujniki).
- Zanonimizowana diagnostyka protokołu i mapy.
- Interfejs po polsku, angielsku, niemiecku, francusku, hiszpańsku i włosku.

## Wymagania

- Home Assistant 2026.7 lub nowszy.
- RE4 dodany wcześniej w aplikacji mobilnej EZVIZ.
- Skonfigurowana i uruchomiona oficjalna integracja **EZVIZ** w HA.
- Dostęp Home Assistanta do chmury EZVIZ.

Integracja korzysta z aktywnej sesji oficjalnej integracji. Nie prosi o drugą
kopię loginu ani hasła EZVIZ i ich nie zapisuje.

## Instalacja przez HACS

1. Otwórz HACS w Home Assistant.
2. Wejdź w **Integracje**, otwórz menu z trzema kropkami i wybierz
   **Niestandardowe repozytoria**.
3. Dodaj `https://github.com/Jameshooper/home-assistant-ezviz-re4` jako typ
   **Integracja**.
4. Wyszukaj **EZVIZ RE4**, wybierz **Pobierz** i uruchom ponownie HA.
5. Otwórz **Ustawienia → Urządzenia i usługi → Dodaj integrację** i wybierz
   **EZVIZ RE4**.
6. Wskaż konto oficjalnej integracji EZVIZ. Numer seryjny zostaw pusty dla
   automatycznego wykrycia albo wpisz go, jeśli konto ma kilka robotów.

## Instalacja ręczna

1. Pobierz kod źródłowy najnowszego wydania z GitHuba.
2. Skopiuj katalog `custom_components/ezviz_re4` do
   `/config/custom_components/` w Home Assistant.
3. Uruchom HA ponownie i dodaj integrację **EZVIZ RE4** z interfejsu.

## Rozwiązywanie problemów

- Jeśli konfiguracja zgłasza brak EZVIZ, najpierw skonfiguruj lub przeładuj
  oficjalną integrację EZVIZ.
- Po aktualizacji uruchom ponownie HA, aby wczytać nowe encje i tłumaczenia.
- Gdy funkcja przestanie działać po aktualizacji EZVIZ, zgłoś wersję HA,
  firmware, model i zanonimizowaną diagnostykę. Nigdy nie publikuj haseł,
  identyfikatorów sesji, kodów weryfikacyjnych ani pełnych logów.

## Licencja

Apache-2.0 — patrz [LICENSE](LICENSE) i [NOTICE](NOTICE). Projekt jest
nieoficjalny i nie jest wspierany ani zatwierdzony przez EZVIZ.
