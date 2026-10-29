#include <SDL.h>
#include <SDL_ttf.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <memory>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int windowWidth = 1024;
constexpr int windowHeight = 768;
constexpr int fireWidth = windowWidth - 300;
constexpr int fireHeight = 400;
constexpr double scale = 2;
// Keskitetään molemmat kerrokset niiden oman piirtoleveyden mukaan.
constexpr int startX = (windowWidth - fireWidth) / 2;
constexpr int glowWidth = static_cast<int>(fireWidth * scale * 2 + 100);
constexpr int glowStartX = (windowWidth - glowWidth) / 2;

// SDL palauttaa C-rajapinnan osoittimia. unique_ptr omistaa resurssin ja kutsuu
// tuhoajaa automaattisesti myös silloin, kun poikkeus keskeyttää suorituksen.
// Näin SDL_DestroyTexture ym. eivät unohdu virhetilanteissa (RAII).
using Window = std::unique_ptr<SDL_Window, decltype(&SDL_DestroyWindow)>;
using Renderer = std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)>;
using Texture = std::unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)>;
using Surface = std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)>;
using Font = std::unique_ptr<TTF_Font, decltype(&TTF_CloseFont)>;

void check(bool ok, const std::string& operation) {
    if (!ok) throw std::runtime_error(operation + ": " + SDL_GetError());
}

struct Libraries {
    Libraries() {
        check(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) == 0, "SDL_Init");
        if (TTF_Init() != 0) {
            const std::string message = TTF_GetError();
            SDL_Quit();
            throw std::runtime_error("TTF_Init: " + message);
        }
    }
    ~Libraries() { TTF_Quit(); SDL_Quit(); }
    Libraries(const Libraries&) = delete;
    Libraries& operator=(const Libraries&) = delete;
};

SDL_Color fireColor(int heat) {
    heat = std::clamp(heat, 0, 255);
    // Listan aaltosulkeet alustavat rakenteen kentät järjestyksessä r,g,b,a.
    // Uint8-muunnos tehdään vasta, kun arvo tiedetään tavun kokoiseksi.
    if (heat < 35) return {0, 0, 0, 255};
    if (heat < 90) return {static_cast<Uint8>(heat * 2), 0, 0, 255};
    if (heat < 150) return {255, static_cast<Uint8>((heat - 90) * 3), 0, 255};
    if (heat < 220)
        return {255, static_cast<Uint8>(180 + heat - 150),
                static_cast<Uint8>((heat - 150) / 2), 255};
    return {255, 245, 210, 255};
}

class Fire {
public:
    void update() {
        for (int x = 0; x < fireWidth; ++x) heat_[fireHeight][x] = random(0, 255);
        // Päivitys tehdään alhaalta ylöspäin kuten Pythonissa. Alempi rivi on
        // siis jo päivitetty, kun seuraava rivi lukee sitä. Silmukan suunnan
        // vaihtaminen tai toinen puskuri muuttaisi liekin etenemisnopeutta.
        for (int y = fireHeight - 1; y > 0; --y) {
            for (int x = 1; x < fireWidth - 1; ++x) {
                const int cooling = random(0, 8);
                const int sourceX = std::clamp(x + random(-1, 1), 1, fireWidth - 2);
                const double average = (heat_[y + 1][sourceX - 1]
                    + heat_[y + 1][sourceX] + heat_[y + 1][sourceX + 1]
                    + heat_[y][x]) / 4.0 / 0.9685;
                // Python ohitti paletin ylittävän indeksin poikkeuksella.
                // Rajaus estää myös C++:n taulukon ulkopuolelle lukemisen.
                heat_[y][x] = std::clamp(static_cast<int>(average - cooling), 0, 255);
            }
        }
    }

    SDL_Color sample(int x, int y) const {
        if (x >= fireWidth || y == 0) return {0, 0, 0, 255};
        return fireColor(heat_[y][x]);
    }

private:
    // std::array on kiinteän kokoinen, oma muistialueensa omistava taulukko.
    // {} nollaa kaikki alkiot. Ylimääräinen alarivi toimii lämmön lähteenä.
    std::array<std::array<int, fireWidth + 1>, fireHeight + 1> heat_{};
    std::mt19937 generator_{std::random_device{}()};
    int random(int low, int high) {
        return std::uniform_int_distribution<int>(low, high)(generator_);
    }
};

// Käytämme tunnettua ARGB8888-pikselimuotoa: jokainen Uint32 sisältää yhden
// pikselin. Bittisiirrot kokoavat värikanavat ilman koneen tavujärjestysoletusta.
Uint32 pack(SDL_Color c) {
    return 0xff000000u | (Uint32{c.r} << 16) | (Uint32{c.g} << 8) | c.b;
}

void composite(std::vector<Uint32>& pixels, const Fire& fire,
               SDL_Rect destination, bool subtract) {
    // Rajataan näkyvä alue ensin: alkuperäisen iso hehku ulottuu ikkunan yli.
    for (int y = std::max(0, destination.y);
         y < std::min(windowHeight, destination.y + destination.h); ++y) {
        for (int x = std::max(0, destination.x);
             x < std::min(windowWidth, destination.x + destination.w); ++x) {
            // Kokonaislukujako tekee saman lähimmän pikselin skaalauksen kuin
            // pygame.transform.scale. Lähteen leveys on liekin todellinen leveys.
            const int sourceX = (x - destination.x) * fireWidth / destination.w;
            const int sourceY = (y - destination.y) * fireHeight / destination.h;
            const SDL_Color source = fire.sample(sourceX, sourceY);
            auto& pixel = pixels[static_cast<std::size_t>(y) * windowWidth + x];
            const auto blend = [subtract](int a, int b) {
                return static_cast<Uint8>(std::clamp(subtract ? a - b : a + b, 0, 255));
            };
            pixel = pack({blend((pixel >> 16) & 255, source.r),
                          blend((pixel >> 8) & 255, source.g),
                          blend(pixel & 255, source.b), 255});
        }
    }
}

struct Letter {
    Texture texture{nullptr, SDL_DestroyTexture};
    int width = 0;
    int height = 0;
};

std::vector<Letter> makeLetters(SDL_Renderer* renderer, TTF_Font* font) {
    std::vector<Letter> letters;
    for (char character : std::string("Happy Flaming June!")) {
        const std::string text(1, character);
        Surface surface(TTF_RenderUTF8_Blended(font, text.c_str(), {255, 255, 255, 255}),
                        SDL_FreeSurface);
        check(surface != nullptr, "Tekstin rasterointi");
        Texture texture(SDL_CreateTextureFromSurface(renderer, surface.get()), SDL_DestroyTexture);
        check(texture != nullptr, "Tekstitekstuuri");
        // unique_ptr ei ole kopioitava. move siirtää omistajuuden vektoriin;
        // paikallinen texture jää tyhjäksi eikä tuhoa siirrettyä tekstuuria.
        letters.push_back({std::move(texture), surface->w, surface->h});
    }
    return letters;
}

void drawText(SDL_Renderer* renderer,
              const std::vector<Letter>& letters,
              Uint64 ticks) {
    constexpr double textScale = 0.95;
    const int y = 100;  // Pienempi arvo nostaa, suurempi laskee.

    // Lasketaan tekstin kokonaisleveys keskittämistä varten.
    int totalWidth = 0;
    for (const auto& letter : letters) {
        totalWidth += std::max(
            1, static_cast<int>(std::round(letter.width * textScale)));
    }

    int x = (windowWidth - totalWidth) / 2;

    for (std::size_t i = 0; i < letters.size(); ++i) {
        const auto& letter = letters[i];

        // Lambda laskee värikanavan ajan ja kirjaimen sijainnin avulla.
        const auto channel = [ticks, i](double phase) {
            return static_cast<Uint8>(
                127 + 127 * std::sin(ticks * 0.004 + i * 0.45 + phase));
        };

        check(SDL_SetTextureColorMod(
                  letter.texture.get(), channel(0), channel(2.1), channel(4.2)) == 0,
              "Tekstin väritys");

        const int w = std::max(
            1, static_cast<int>(std::round(letter.width * textScale)));
        const int h = std::max(
            1, static_cast<int>(std::round(letter.height * textScale)));

        SDL_Rect destination{x, y, w, h};

        // Tavallinen kopiointi piirtää kirjaimen ilman kiertoa.
        check(SDL_RenderCopy(renderer, letter.texture.get(),
                             nullptr, &destination) == 0,
              "Tekstin piirto");

        x += w;  // Seuraava kirjain oikealle.
    }
}

}
// namespace

int main(int argc, char** argv) {
    try {
        int frameLimit = 0;
        std::filesystem::path fontPath;
        // Rajattu ajo mahdollistaa käynnistyksen tarkistamisen ilman, että
        // testin täytyy painaa Esc-näppäintä. Tavallinen ajo jatkuu sulkemiseen.
        for (int i = 1; i < argc; ++i) {
            const std::string argument = argv[i];
            if (argument == "--frames" && i + 1 < argc) {
                frameLimit = std::stoi(argv[++i]);
                if (frameLimit <= 0) throw std::runtime_error("--frames tarvitsee positiivisen luvun");
            } else if (argument == "--font" && i + 1 < argc) fontPath = argv[++i];
            else throw std::runtime_error("Käyttö: flaming-june [--frames N] [--font TIEDOSTO]");
        }
        Libraries libraries;
        Window window(SDL_CreateWindow("Flaming June — C++ / SDL2", SDL_WINDOWPOS_CENTERED,
                      SDL_WINDOWPOS_CENTERED, windowWidth, windowHeight, SDL_WINDOW_SHOWN), SDL_DestroyWindow);
        check(window != nullptr, "Ikkunan luonti");
        Renderer renderer(SDL_CreateRenderer(window.get(), -1, SDL_RENDERER_ACCELERATED), SDL_DestroyRenderer);
        if (!renderer) renderer.reset(SDL_CreateRenderer(window.get(), -1, SDL_RENDERER_SOFTWARE));
        check(renderer != nullptr, "Piirtäjän luonti");
        if (fontPath.empty()) {
            // SDL:n hakemisto vapautetaan SDL_free:llä, ei C++:n delete:llä.
            std::unique_ptr<char, decltype(&SDL_free)> base(SDL_GetBasePath(), SDL_free);
            fontPath = base ? std::filesystem::path(base.get()) / "VINERITC.TTF" : "VINERITC.TTF";
            if (!std::filesystem::exists(fontPath)) fontPath = "VINERITC.TTF";
        }
        Font font(TTF_OpenFont(fontPath.string().c_str(), 36), TTF_CloseFont);
        check(font != nullptr, "Fontin avaaminen (" + fontPath.string() + ")");
        auto letters = makeLetters(renderer.get(), font.get());
        Texture frame(SDL_CreateTexture(renderer.get(), SDL_PIXELFORMAT_ARGB8888,
                      SDL_TEXTUREACCESS_STREAMING, windowWidth, windowHeight), SDL_DestroyTexture);
        check(frame != nullptr, "Kuvatekstuuri");
        check(SDL_SetTextureBlendMode(frame.get(), SDL_BLENDMODE_ADD) == 0, "Lisäävä sekoitus");
        std::vector<Uint32> pixels(windowWidth * windowHeight);
        Fire fire;
        bool running = true;
        int frames = 0;
        while (running && (frameLimit == 0 || frames < frameLimit)) {
            const Uint64 frameStart = SDL_GetTicks64();
            SDL_Event event{};
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT ||
                    (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE)) running = false;
            }
            if (!running) break;
            fire.update();
            std::fill(pixels.begin(), pixels.end(), 0xff000000u);
            composite(pixels, fire, {startX, windowHeight - static_cast<int>(fireHeight * scale),
                      fireWidth, static_cast<int>(fireHeight * scale)}, false);
            // PyGamen BLEND_RGBA_SUB vähentää RGB-kanavat; set_alpha ei tee
            // siitä tavallista läpinäkyvää hehkua. Tehdään vähennys CPU:lla,
            // koska SDL2:n perussekoitustiloissa ei ole vähennystilaa.
            composite(pixels, fire, {glowStartX,
                      windowHeight - static_cast<int>(fireHeight * scale * 3),
                      glowWidth, static_cast<int>(fireHeight * scale * 2)}, true);
            check(SDL_UpdateTexture(frame.get(), nullptr, pixels.data(), windowWidth * sizeof(Uint32)) == 0,
                  "Pikselien siirto");
            check(SDL_SetRenderDrawColor(renderer.get(), 0, 0, 0, 255) == 0, "Taustaväri");
            check(SDL_RenderClear(renderer.get()) == 0, "Ruudun tyhjennys");
            drawText(renderer.get(), letters, frameStart);
            check(SDL_RenderCopy(renderer.get(), frame.get(), nullptr, nullptr) == 0, "Liekin piirto");
            SDL_RenderPresent(renderer.get());
            ++frames;
            // Efekti päivittyy ruuduittain kuten Pythonissa. Liian nopea silmukka
            // muuttaisi animaatiota, joten rajoitamme nopeuden noin 159 FPS:ään.
            const double remaining = 1000.0 / 60.0 - (SDL_GetTicks64() - frameStart);
            if (remaining > 0) SDL_Delay(static_cast<Uint32>(std::ceil(remaining)));
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Virhe: " << error.what() << '\n';
        return 1;
    }
}
