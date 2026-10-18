# Flaming-June
Happy June to everyone!

## C++ / SDL2 -versio

`flaming_june-mod.cpp` on Python-version `flaming_june-mod.py` pohjalta tehty
C++17-toteutus. Vaikeammat kohdat on kommentoitu suomeksi. Alkuperäiset
Python-tiedostot ja erillinen `liekki.cpp` eivät muutu.

Tarvitset C++-kääntäjän, CMake:n, pkg-configin, SDL2:n ja SDL2_ttf:n.
Arch Linuxissa paketit ovat `base-devel cmake pkgconf sdl2 sdl2_ttf`.

Käännä ja käynnistä projektin hakemistossa:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
./build/flaming-june
```

Esc tai ikkunan sulkeminen lopettaa ohjelman. CMake kopioi `VINERITC.TTF`-fontin
ohjelman viereen. Toisen fontin voi antaa parametrina:

```bash
./build/flaming-june --font /polku/fonttiin.ttf
```

### Mitä koodista kannattaa opiskella?

1. `main`: tapahtumasilmukka lukee näppäimet, päivittää simulaation ja piirtää
   kuvan. Tämä on sama perusrakenne kuin PyGamessa.
2. `Fire::update`: sisäkkäiset `std::array`-taulukot vastaavat Pythonin
   lämpöruudukkoa. Päivitysjärjestys vaikuttaa simulaatioon.
3. `fireColor` ja `composite`: lämpö muuttuu RGB-väriksi, skaalataan ja
   yhdistetään ruudun pikseleihin. `Uint32`, bittisiirrot ja lambda-funktio
   on selitetty kommenteissa.
4. `makeLetters` ja `drawText`: kirjaimet rasteroidaan vain kerran ja väritetään
   joka ruudulla sinifunktioilla. Kierto huomioi SDL:n ja PyGamen eri suunnat.
5. `unique_ptr` ja `Libraries`: RAII vapauttaa resurssit automaattisesti.
   `.get()` lainaa osoittimen SDL-kutsulle; `std::move` siirtää omistajuuden.

### Erot Python-versioon

- Lämpö rajataan välille 0–255. Pythonin paletin ylittävä indeksi jätti pikselin
  vanhaan väriin; C++-versio käyttää kuuminta sallittua väriä.
- Käyttämättömät muuttujat, satunnainen alpha-taulukko ja yhden suorakulmion
  ylimääräinen piirto on jätetty pois. Kuva on peittävä RGB-liekkipinta.
- Alkuperäisen hehkun `BLEND_RGBA_SUB` on vähentävä väriyhdistely, joten myös
  tässä iso kerros vähentää RGB-kanavia. Kyse ei ole tavallisesta alpha-hehkusta.
- Tekstin kaksinkertainen identtinen piirto on korvattu yhdellä piirrolla.
  SDL_ttf:n rasterointi ja satunnaisluvut voivat poiketa PyGamesta; tarkoitus
  on säilyttää efekti, ei tuottaa pikselilleen samaa kuvaa.
- Ruudunpäivitys on rajoitettu noin 159 FPS:ään. Simulaatio etenee ruuduittain
  kuten alkuperäinen, joten hitaalla koneella myös animaatio hidastuu.

### Käynnistystarkistus ilman näyttöä

```bash
SDL_VIDEODRIVER=dummy ./build/flaming-june --frames 120
```

`--frames N` lopettaa N ruudun jälkeen. Näytötön tarkistus varmistaa alustuksen,
fontin latauksen ja piirto-/simulaatiosilmukan toiminnan, mutta ei ulkoasua.
