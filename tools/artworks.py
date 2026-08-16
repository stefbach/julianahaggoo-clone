#!/usr/bin/env python3
"""The catalogue: every work, in the order it should appear in the portfolio.

This table is the single source of truth for the whole site. Adding a painting
here and re-running the build is all it takes to publish it.
"""
from __future__ import annotations

from dataclasses import dataclass

ROOT_MARKER = "portfolio.html"


@dataclass(frozen=True)
class Art:
    slug: str          # url + generated file names
    title: str
    page: str          # the artwork's own page
    thumb: str         # rendition shown on the old site — the framing to keep
    medium: str        # "Oil" | "Acrylic"
    year: int
    size: str
    price: str = ""
    sold: bool = False

    @property
    def status(self) -> str:
        return "sold" if self.sold else "available"

    @property
    def tag(self) -> str:
        return "Sold" if self.sold else (self.price or "On request")

    @property
    def cartel(self) -> list[str]:
        """The museum label, in reading order."""
        return [f"{self.medium} painting", str(self.year), self.size]


ARTWORKS: list[Art] = [
    Art("summer-2025", "Summer", "summer-2025.html", "images/summer.png", "Oil", 2025, "120 × 120 × 3 cm", "€2900"),
    Art("the-red", "The Red", "the-red.html", "images/THE RED 1.png", "Oil", 2025, "130 × 130 cm", sold=True),
    Art("breath-of-light", "Breath of Light", "Breath-of-Light.html", "images/Breath-of-Light.png", "Oil", 2025, "100 × 100 cm", sold=True),
    Art("the-blue", "The Blue", "the-blue.html", "images/the_blue.png", "Oil", 2025, "120 × 120 cm", sold=True),
    Art("earth-vision", "Earth Vision", "Earth-vision.html", "images/Les-deux-tableaux-portfolio.png", "Oil", 2025, "65 × 100 × 3 cm", "€2600"),
    Art("serenity-of-motion", "Serenity of Motion", "serenity-of-motion.html", "images/serenity-of-motion-imageneavant.png", "Oil", 2025, "130 × 130 × 3 cm", "€3800"),
    Art("flow-of-energy", "Flow of Energy", "flow-of-energy.html", "images/FLOW-OF-ENERGY.png", "Oil", 2024, "100 × 100 × 3 cm", "€2300"),
    Art("whispers-of-pink", "Whispers of Pink", "whispers-of-pink.html", "images/WHISPERS-OF-PINK.png", "Oil", 2024, "100 × 100 × 3 cm", "€2200"),
    Art("blue-shadows", "Blue Shadows", "blue-shadows.html", "images/BLUE-SHADOWS.png", "Oil", 2024, "100 × 100 × 3 cm", "€2400"),
    Art("passion-palette", "Passion Palette", "passion-palette.html", "images/image-04-442x332.png", "Oil", 2023, "150 × 200 × 5 cm", "€6700"),
    Art("midnight-whispers", "Midnight Whispers", "midnight-whispers.html", "images/image-11.png", "Oil", 2023, "150 × 100 × 3 cm", sold=True),
    Art("sensuality", "Sensuality", "sensuality.html", "images/sensuality-07.webp", "Oil", 2023, "150 × 150 × 5 cm", "€5400"),
    Art("feeling-flow", "Feeling Flow", "feeling-flow.html", "images/image-18.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2200"),
    Art("blue-bubble", "Blue Bubble", "blue-bubble.html", "images/image-23.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2300"),
    Art("sunset-silhouettes", "Sunset Silhouettes", "sunset-silhouettes.html", "images/image-24.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2300"),
    Art("deep-blue-lagoon", "Deep Blue Lagoon", "deep-blue-lagoon.html", "images/image-25.webp", "Oil", 2023, "100 × 100 × 3 cm", sold=True),
    Art("the-dark-and-light", "The Dark and Light", "the-dark-and-light.html", "images/image-29.webp", "Oil", 2023, "100 × 120 × 3 cm", "€2400"),
    Art("harmony", "Harmony", "harmony.html", "images/harmony-2.png", "Oil", 2023, "60 × 80 × 2 cm", sold=True),
    Art("rise-like-a-sun", "Rise Like a Sun", "rise-like-a-sun.html", "images/image-09-442x332.webp", "Oil", 2022, "100 × 100 × 4 cm", sold=True),
    Art("the-curve", "The Curve", "the-curve.html", "images/image-08-442x442.webp", "Oil", 2022, "100 × 100 × 4 cm", "€2300"),
    Art("in-shades-of-pink", "In Shades of Pink", "in-shades-of-pink.html", "images/image-2-442x332.webp", "Acrylic", 2022, "100 × 120 × 3 cm", "€2000"),
    Art("blue-white", "Blue White", "blue-white.html", "images/image-21-442x332.webp", "Oil", 2022, "100 × 100 × 4 cm", sold=True),
    Art("waves", "Waves", "waves.html", "images/image-21.webp", "Oil", 2022, "100 × 120 × 2 cm", "€2400"),
    Art("deep-blue", "Deep Blue", "deep-blue.html", "images/image-27.webp", "Acrylic", 2022, "100 × 120 × 3 cm", "€1900"),
    Art("the-wall", "The Wall", "the-wall.html", "images/image-28.webp", "Oil", 2022, "100 × 100 × 2 cm", "€2200"),
    Art("summer-2022", "Summer", "summer.html", "images/image-30.webp", "Oil", 2022, "80 × 60 × 4 cm", sold=True),
    Art("intensity", "Intensity", "intensity.html", "images/image-31.webp", "Oil", 2022, "60 × 80 × 4 cm", "€1500"),
    Art("the-7-hearts", "The 7 Hearts", "the-7-hearts.html", "images/image-32.webp", "Oil", 2022, "100 × 120 × 4 cm", "€2300"),
    Art("nightfall", "Nightfall", "nightfall.html", "images/image-05.webp", "Oil", 2021, "80 × 80 × 4 cm", "€1600"),
    Art("the-white-cross", "The White Cross", "the-white-cross.html", "images/image-3-442x332.webp", "Oil", 2020, "80 × 100 × 2 cm", "€1700"),
    Art("the-red-wall", "The Red Wall", "the-red-wall.html", "images/image-22.webp", "Oil", 2019, "97 × 130 × 2 cm", "€2500"),
    Art("freedom-and-love", "Freedom and Love", "freedom-and-love.html", "images/image-06.webp", "Oil", 2013, "100 × 100 × 4 cm", sold=True),
    Art("fly-like-a-bird", "Fly Like a Bird", "fly-like-a-bird.html", "images/image-07.webp", "Oil", 2012, "100 × 100 × 4 cm", sold=True),
    Art("the-circle", "The Circle", "the-circle.html", "images/image-16.webp", "Oil", 2012, "100 × 100 × 4 cm", "€2100"),
    Art("mystic-flames", "Mystic Flames", "mystic-flames.html", "images/image-14.webp", "Oil", 2010, "100 × 100 × 2 cm", "€2200"),
    Art("winter", "Winter", "winter.html", "images/image-12.webp", "Oil", 2009, "54 × 65 × 2 cm", "€1500"),
]

# Everything on the site that is not a painting.
PAGE_IMAGES = {
    "portrait": "images/V2-2-About-Me.png",
    "event-exhibition": "images/Cover-Event-2.png",
    "event-temptation": "images/the-temptation.png",
}

# The home carousel — the artist beside her own canvases, the three plates the
# original site opened on. `focus` is the object-position: these are portraits,
# so the crop is anchored on her, never on the middle of the frame.
HOME_SLIDES = [
    {
        "key": "slide-monochrome",
        "src": "images/image2-04-1920x1080.jpeg",
        "alt": "Juliana Haggoo beside a black and white canvas",
        "caption": "Serenity of Motion",
        "focus": "center 42%",
    },
    {
        "key": "slide-studio",
        "src": "images/coverslider3.png",
        "alt": "Juliana Haggoo in front of a blue and red canvas",
        "caption": "In the studio",
        "focus": "center 28%",
    },
]

EXHIBITION_PHOTOS = [f"images/Art-Exhibition-Gallery-{i}.jpg" for i in range(1, 19)]

STUDIO = {
    "name": "Juliana Haggoo",
    "role": "Artist Painter",
    "email": "jh@julianahaggoo.art",
    "phone": "+33 6 65 08 75 60",
    "phone_href": "tel:+33665087560",
    "instagram": "https://www.instagram.com/julianahaggooart/",
    "site": "https://www.julianahaggoo.art",
}


# The plates each artwork page showed in the original build: the canvas itself and
# the photographs of it hanging. Captured here so the image build never depends on
# markup it is about to regenerate.
PLATES: dict[str, list[str]] = {
    "summer-2025": [
        "images/summer.png",
        "images/summer-mock-up.jpg",
    ],
    "the-red": [
        "images/THE RED 1.png",
        "images/THE RED 2.png",
        "images/THE RED 3.jpg",
    ],
    "breath-of-light": [
        "images/Breath-of-Light.png",
        "images/Breath-of-Light-mock-up.jpg",
    ],
    "the-blue": [
        "images/the_blue.png",
        "images/the_blue_2.jpg",
    ],
    "earth-vision": [
        "images/Les-deux-tableaux-portfolio.png",
        "images/3-portfolio-earth-Blanc.png",
        "images/Bleu.png",
        "images/Earthvsion-environment.jpg",
    ],
    "serenity-of-motion": [
        "images/serenity-of-motion-imageneavant.png",
        "images/serenity-of-motion-gallery-2.jpg",
        "images/serenity-of-motion-gallery-3.jpg",
    ],
    "flow-of-energy": [
        "images/FLOW-OF-ENERGY.png",
        "images/FLOW-OF-ENERGY-gallery4.jpg",
        "images/FLOW-OF-ENERGY-gallery3.jpg",
        "images/FLOW-OF-ENERGY-gallery2.jpg",
    ],
    "whispers-of-pink": [
        "images/WHISPERS-OF-PINK.png",
        "images/WHISPERS-OF-PINK-gallery1.jpg",
        "images/whispers-of-pink-environment2.jpg",
    ],
    "blue-shadows": [
        "images/BLUE-SHADOWS.png",
        "images/blue-shadows-5.jpg",
        "images/blue-shadows-6.jpg",
    ],
    "passion-palette": [
        "images/passion-palette-07-1387x925.png",
        "images/passion-palette-gallery-2.jpg",
        "images/image-21-1387x925.jpg",
    ],
    "midnight-whispers": [
        "images/midnight-whispers-21-1387x925.png",
        "images/midnight-whispers-09-1387x925.png",
        "images/midnight-environment.jpg",
    ],
    "sensuality": [
        "images/sensuality-21-1387x925.png",
        "images/sensuality-environment.jpg",
        "images/winter-07-1387x925.png",
    ],
    "feeling-flow": [
        "images/feeling-flow-21-1387x925.png",
        "images/feeling-flow-09-1387x925.png",
        "images/feelingflow-environment.jpg",
    ],
    "blue-bubble": [
        "images/blue-bubble-07-1387x925.png",
        "images/blue-bubble-09-1070x1065.jpg",
    ],
    "sunset-silhouettes": [
        "images/sunset-silhouettes-21-1387x925.png",
        "images/sunset-silhouettes-07-1387x925.png",
        "images/sunsetsilhouettes-environment.jpg",
    ],
    "deep-blue-lagoon": [
        "images/deep-blue-lagoon-21-1387x925.png",
        "images/deep-blue-lagoon-07-1387x925.png",
        "images/deepbluelagoon-environment.jpg",
    ],
    "the-dark-and-light": [
        "images/the-dark-and-light-21-1387x925.png",
        "images/the-dark-and-light-09-1387x925.png",
        "images/the-dark-and-light-environment.jpg",
    ],
    "harmony": [
        "images/harmony-3.png",
        "images/harmony.png",
        "images/harmony-environment.jpg",
    ],
    "rise-like-a-sun": [
        "images/rise-like-a-sun-21-1387x925.png",
        "images/rise-like-a-sun-09-1387x925.png",
        "images/rise-like-a-sun-07-1387x925.png",
        "images/rise-like-a-sun-4.webp",
    ],
    "the-curve": [
        "images/the-curve-21-1387x925.png",
        "images/the-curve-gallery-5.jpg",
        "images/the-curve-4.webp",
    ],
    "in-shades-of-pink": [
        "images/in-shades-of-pink-21-1387x925.png",
        "images/in-shades-of-pink-09-1387x925.png",
        "images/shadeinpink-environment.jpg",
        "images/in-shades-of-pink-4.webp",
    ],
    "blue-white": [
        "images/blue-white-21-1387x925.png",
        "images/blue-white-07-1387x925.png",
        "images/bluewhite-environment.jpg",
    ],
    "waves": [
        "images/waves-21-1387x925.png",
        "images/waves-09-1387x925.png",
        "images/waves-4.webp",
        "images/waves-environment.jpg",
    ],
    "deep-blue": [
        "images/deep-blue-21-1387x925.png",
        "images/deep-blue-09-1387x925.png",
        "images/deepblue-environment.jpg",
    ],
    "the-wall": [
        "images/the-wall-21-1387x925.png",
        "images/the-wall-09-1387x925.png",
        "images/the-wall-4.webp",
        "images/thewall-environment.jpg",
    ],
    "summer-2022": [
        "images/summer-21-1387x925.png",
        "images/summer-07-1387x925.png",
        "images/summer-4.webp",
    ],
    "intensity": [
        "images/intensity-21-1387x925.png",
        "images/intensity-09-1387x925.png",
        "images/intensity-07-1387x925.png",
    ],
    "the-7-hearts": [
        "images/the-7-hearts-21-1387x925.png",
        "images/the-7-hearts-09-1387x925.png",
        "images/the7hearts-environment.jpg",
        "images/the-7-hearts-4.webp",
    ],
    "nightfall": [
        "images/nightfall-07-1387x925.png",
        "images/nightfall-09-1387x925.png",
        "images/nightfall-4.webp",
        "images/nightfall-21-1387x925.png",
    ],
    "the-white-cross": [
        "images/the-white-cross-21-1387x925.png",
        "images/the-white-cross-09-1387x925.png",
        "images/the-white-cross-4.webp",
        "images/thewritecross-environment.jpg",
    ],
    "the-red-wall": [
        "images/the-red-wall-21-1387x925.png",
        "images/the-red-wall-09-1387x925.png",
        "images/the-red-wall-4.webp",
        "images/theredwall-environment.jpg",
    ],
    "freedom-and-love": [
        "images/freedom-and-love-21-1387x925.png",
        "images/freedom-and-love-09-1387x925.png",
        "images/freedom-and-love-4.webp",
    ],
    "fly-like-a-bird": [
        "images/fly-like-a-bird-21-1387x925.png",
        "images/fly-like-a-bird-09-1387x925.png",
        "images/fly-like-a-bird-07-1387x925.png",
        "images/fly-like-a-bird-4.webp",
    ],
    "the-circle": [
        "images/the-circle-21-1387x925.png",
        "images/the-circle-09-1387x925.png",
        "images/The-circle-environment.jpg",
        "images/the-circle-4.webp",
    ],
    "mystic-flames": [
        "images/mystic-flames-21-1387x925.png",
        "images/mystic-flames-07-1387x925.png",
        "images/mystic-flames-4.webp",
    ],
    "winter": [
        "images/winter-21-1387x925.png",
        "images/winter-09-1387x925.png",
        "images/winter-07-1387x925.png",
    ],
}
