# EZVIZ RS20 Pro dla Home Assistanta

Polski · [English](README.md)

Nieoficjalna integracja Home Assistanta dla robota **EZVIZ RS20 Pro** i jego
stacji bazowej. Przetestowana z modelem `CS-RS20-PRO-PGA2`.

> Projekt jest eksperymentalny i korzysta z usług chmurowych rozpoznanych w
> aplikacji EZVIZ, ponieważ producent nie publikuje API robota. Zmiana chmury
> lub oprogramowania może czasowo wyłączyć część funkcji.

## Funkcje

- Start, pauza, zatrzymanie i powrót robota do stacji.
- Natywny wybór pomieszczeń i sprzątanie pokoi w Home Assistant.
- Czujniki baterii, posprzątanej powierzchni i zużycia materiałów.
- Stan stacji: mycie i suszenie mopów, opróżnianie kurzu i zbiornika oraz
  wykrycie opcjonalnego modułu dopływu i odpływu wody.
- Ustawienia stacji: blokada rodzicielska, automatyczne opróżnianie kurzu,
  dozowanie płynu i samooczyszczanie szczotki obrotowej.
- Zdjęcie z kamery robota wykonywane wyłącznie na wyraźne żądanie.
- Zanonimizowana diagnostyka protokołu, mapy i kamery.
- Interfejs po polsku, angielsku, niemiecku, francusku, hiszpańsku i włosku.

Ręczne komendy uruchamiające grzałkę, pompę lub silnik odpylania nie są
udostępnione, dopóki ich protokół nie zostanie jednoznacznie potwierdzony.
Przełączniki ustawień nie uruchamiają cyklu konserwacji podczas startu HA.

## Wymagania

- Home Assistant 2026.7 lub nowszy.
- RS20 Pro dodany wcześniej w aplikacji mobilnej EZVIZ.
- Skonfigurowana i uruchomiona oficjalna integracja **EZVIZ** w HA.
- Dostęp Home Assistanta do chmury EZVIZ.

Integracja korzysta z aktywnej sesji oficjalnej integracji. Nie prosi o drugą
kopię loginu ani hasła EZVIZ i ich nie zapisuje.

## Instalacja przez HACS

1. Otwórz HACS w Home Assistant.
2. Wejdź w **Integracje**, otwórz menu z trzema kropkami i wybierz
   **Niestandardowe repozytoria**.
3. Dodaj `https://github.com/Jameshooper/home-assistant-ezviz-rs20-pro` jako typ
   **Integracja**.
4. Wyszukaj **EZVIZ RS20 Pro**, wybierz **Pobierz** i uruchom ponownie HA.
5. Otwórz **Ustawienia → Urządzenia i usługi → Dodaj integrację** i wybierz
   **EZVIZ RS20 Pro**.
6. Wskaż konto oficjalnej integracji EZVIZ. Numer seryjny zostaw pusty dla
   automatycznego wykrycia albo wpisz go, jeśli konto ma kilka robotów.

## Instalacja ręczna

1. Pobierz kod źródłowy najnowszego wydania z GitHuba.
2. Skopiuj katalog `custom_components/ezviz_rs20pro` do
   `/config/custom_components/` w Home Assistant.
3. Uruchom HA ponownie i dodaj integrację **EZVIZ RS20 Pro** z interfejsu.

## Prywatność kamery

Encja obrazu przechowuje w pamięci tylko ostatnią klatkę. Kamera jest otwierana
na kilka sekund wyłącznie po wywołaniu akcji
`ezviz_rs20pro.refresh_camera_snapshot`, po czym transmisja jest zamykana.
Integracja nie nagrywa stale, nie zapisuje zdjęć na dysku i nie uruchamia kamery
automatycznie.

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
