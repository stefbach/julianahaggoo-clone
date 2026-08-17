#!/usr/bin/env python3
"""Every word the site says, in both languages.

English lives at the root so the live URLs never moved; French lives under /fr/.
The titles of the paintings are proper names and are never translated — a gallery
label does not rename a canvas — but the medium, the status and every piece of
furniture around them are.
"""
from __future__ import annotations

LOCALES = ("en", "fr")
DEFAULT = "en"

# Where each locale's pages sit, and how deep they are from the repository root.
HOME = {"en": "", "fr": "fr/"}
UP = {"en": "", "fr": "../"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "html_lang": "en",
        "language_name": "English",
        "language_switch": "Français",
        "language_switch_label": "Voir ce site en français",
        "role": "Artist Painter",
        "based": "Paris &amp; Mauritius",

        "nav_home": "Home",
        "nav_about": "About",
        "nav_about_long": "About Me",
        "nav_portfolio": "Portfolio",
        "nav_events": "Events",
        "nav_contact": "Contact",
        "nav_temptation": "Dark &amp; Light: The Temptation",
        "brand_label": "home",
        "menu_open": "Open menu",
        "menu_close": "Close menu",
        "nav_primary": "Primary",
        "nav_primary_mobile": "Primary, mobile",
        "skip": "Skip to content",

        "footer_cta": "Interested in a canvas?",
        "footer_cta_link": "Write to the studio.",
        "footer_studio": "Studio",
        "footer_explore": "Explore",
        "footer_rights": "All works and images are the property of the artist.",

        "home_title": "Juliana Haggoo — Artist Painter",
        "home_description": ("Abstract oil and acrylic paintings by Juliana Haggoo. Colour built up "
                             "in layers, painted at night to music."),
        "home_quote": "“It is at night, with music, that my creativity fully blossoms.”",
        "home_see_works": "See the {n} works",
        "home_latest": "Latest work",
        "home_open_work": "Open the work",
        "home_selected": "Selected works",
        "home_all_works": "All works",
        "home_the_artist": "The artist",
        "home_about_heading": "From the stage to the canvas",
        "home_about_1": ("My artistic journey began in 2005 when I joined a jazz band in Paris. "
                         "Painting then became my outlet in 2007 — I immersed myself in abstract "
                         "art, letting my emotions flow onto the canvas."),
        "home_about_2": ("Today, my journey fuses music, dance and painting. It exemplifies "
                         "resilience and the liberating power of art."),
        "home_about_button": "About the artist",
        "home_studio_alt": "Juliana Haggoo in the studio",

        "about_title": "About Me — Juliana Haggoo",
        "about_description": ("Juliana Haggoo on jazz, cabaret, and the night-time painting practice "
                              "that became her life's work."),
        "about_heading": "About Me",
        "about_quote": ("“I immersed myself in the world of the abstract, letting my emotions and "
                        "stress dissolve into the colors and shapes on the canvas.”"),
        "about_portrait_alt": "Portrait of Juliana Haggoo",
        "about_button": "See the works",

        "portfolio_title": "Portfolio — Juliana Haggoo",
        "portfolio_description": ("The complete body of work of Juliana Haggoo — {n} oil and acrylic "
                                  "paintings from {first} to {last}."),
        "portfolio_heading": "Portfolio",
        "portfolio_lede": "Oil and acrylic on canvas, {first}–{last}.",
        "portfolio_count": "{n} works",
        "portfolio_count_one": "{n} work",
        "portfolio_available": "{n} available",
        "filter_medium": "Filter by medium",
        "filter_availability": "Filter by availability",
        "filter_all": "All",
        "filter_available": "Available only",
        "filter_year": "Year",
        "filter_all_years": "All years",
        "filter_order": "Order",
        "order_recent": "Most recent",
        "order_oldest": "Earliest first",
        "order_title": "A – Z",
        "empty": "No work matches this selection.",
        "empty_reset": "Show every work",

        "work_description": "{title}, {medium} on canvas, {year}, {size}. By Juliana Haggoo.",
        "work_medium": "Medium",
        "work_year": "Year",
        "work_dimensions": "Dimensions",
        "work_status": "Status",
        "work_on_canvas": "{medium} on canvas",
        "work_enquire": "Enquire about this work",
        "work_enquiry_subject": "Enquiry — {title} ({year})",
        "work_back": "Back to the portfolio",
        "work_in_situ": "In situ",
        "work_more": "More works",
        "work_previous": "Previous",
        "work_next": "Next",
        "work_enlarge": "Enlarge {title}",
        "work_enlarge_view": "Enlarge view {n} of {title}",
        "work_view_alt": "{title} — view {n}",
        "work_alt": "{title} — {medium} painting, {year}",
        "work_nav": "Works",
        "sold": "Sold",
        "on_request": "On request",
        "medium_oil": "Oil",
        "medium_acrylic": "Acrylic",
        "painting": "painting",

        "events_title": "Events — Juliana Haggoo",
        "events_description": ("Exhibitions and films by Juliana Haggoo, including Noho House "
                               "Gallery Barcelona, January 2025."),
        "events_heading": "Events",
        "event_exhibition": "Art Exhibition",
        "event_exhibition_venue": "Noho House Gallery, Barcelona",
        "event_exhibition_date": "January 23, 2025",
        "event_temptation": "Dark &amp; Light as the love: the Temptation",
        "event_temptation_kind": "A film",

        "exhibition_title": "Art Exhibition, Barcelona — Juliana Haggoo",
        "exhibition_description": "Art Exhibition — January 23, 2025, at Noho House Gallery, Barcelona.",
        "exhibition_film_note": "Film from the opening — press play to load it.",
        "exhibition_evening": "The evening",
        "exhibition_photographs": "{n} photographs",
        "exhibition_photo_alt": "Art exhibition at Noho House Gallery, Barcelona — photograph {n}",
        "exhibition_enlarge": "Enlarge photograph {n}",

        "temptation_title": "Dark & Light as the love: the Temptation — Juliana Haggoo",
        "temptation_description": "Dark & Light as the love: the Temptation — a film by Juliana Haggoo.",
        "temptation_heading": "Dark &amp; Light as the love:<br>the Temptation",
        "temptation_note": "Press play to load the film.",
        "temptation_back": "Back to events",

        "viewer_label": "Image viewer",
        "viewer_close": "Close viewer",
        "viewer_prev": "Previous image",
        "viewer_next": "Next image",
        "viewer_open": "Open the work",

        "slider_label": "Juliana Haggoo and her work",
        "slider_prev": "Previous slide",
        "slider_next": "Next slide",
        "slider_dots": "Choose a slide",
        "slider_goto": "Go to slide {n}",
        "slider_pause": "Pause",
        "slider_play": "Play",
        "slider_pause_label": "Pause the carousel",
        "slider_play_label": "Play the carousel",
        "slider_status": "Slide {n} of {total}",
        "slide_monochrome_alt": "Juliana Haggoo beside a black and white canvas",
        "slide_monochrome_caption": "Serenity of Motion",
        "slide_studio_alt": "Juliana Haggoo in front of a blue and red canvas",
        "slide_studio_caption": "In the studio",
    },

    "fr": {
        "html_lang": "fr",
        "language_name": "Français",
        "language_switch": "English",
        "language_switch_label": "View this site in English",
        "role": "Artiste Peintre",
        "based": "Paris &amp; Maurice",

        "nav_home": "Accueil",
        "nav_about": "À propos",
        "nav_about_long": "À propos",
        "nav_portfolio": "Portfolio",
        "nav_events": "Événements",
        "nav_contact": "Contact",
        "nav_temptation": "Dark &amp; Light : The Temptation",
        "brand_label": "accueil",
        "menu_open": "Ouvrir le menu",
        "menu_close": "Fermer le menu",
        "nav_primary": "Principale",
        "nav_primary_mobile": "Principale, mobile",
        "skip": "Aller au contenu",

        "footer_cta": "Une toile vous intéresse ?",
        "footer_cta_link": "Écrivez à l’atelier.",
        "footer_studio": "Atelier",
        "footer_explore": "Explorer",
        "footer_rights": "Toutes les œuvres et images sont la propriété de l’artiste.",

        "home_title": "Juliana Haggoo — Artiste Peintre",
        "home_description": ("Peintures abstraites à l’huile et à l’acrylique de Juliana Haggoo. "
                             "La couleur posée en couches, peinte la nuit, en musique."),
        "home_quote": "« C’est la nuit, en musique, que ma créativité s’épanouit pleinement. »",
        "home_see_works": "Voir les {n} œuvres",
        "home_latest": "Dernière œuvre",
        "home_open_work": "Voir l’œuvre",
        "home_selected": "Œuvres choisies",
        "home_all_works": "Toutes les œuvres",
        "home_the_artist": "L’artiste",
        "home_about_heading": "De la scène à la toile",
        "home_about_1": ("Mon parcours artistique a commencé en 2005, lorsque j’ai rejoint un groupe "
                         "de jazz à Paris. La peinture est ensuite devenue mon exutoire en 2007 — je "
                         "me suis plongée dans l’art abstrait, laissant mes émotions se déverser sur "
                         "la toile."),
        "home_about_2": ("Aujourd’hui, mon chemin réunit la musique, la danse et la peinture. Il dit "
                         "la résilience et le pouvoir libérateur de l’art."),
        "home_about_button": "À propos de l’artiste",
        "home_studio_alt": "Juliana Haggoo dans son atelier",

        "about_title": "À propos — Juliana Haggoo",
        "about_description": ("Juliana Haggoo : le jazz, le cabaret, et cette peinture de nuit "
                              "devenue l’œuvre d’une vie."),
        "about_heading": "À propos",
        "about_quote": ("« Je me suis plongée dans le monde de l’abstrait, laissant mes émotions et "
                        "mon stress se dissoudre dans les couleurs et les formes de la toile. »"),
        "about_portrait_alt": "Portrait de Juliana Haggoo",
        "about_button": "Voir les œuvres",

        "portfolio_title": "Portfolio — Juliana Haggoo",
        "portfolio_description": ("L’œuvre complète de Juliana Haggoo — {n} peintures à l’huile et à "
                                  "l’acrylique, de {first} à {last}."),
        "portfolio_heading": "Portfolio",
        "portfolio_lede": "Huile et acrylique sur toile, {first}–{last}.",
        "portfolio_count": "{n} œuvres",
        "portfolio_count_one": "{n} œuvre",
        "portfolio_available": "{n} disponibles",
        "filter_medium": "Filtrer par technique",
        "filter_availability": "Filtrer par disponibilité",
        "filter_all": "Toutes",
        "filter_available": "Disponibles seulement",
        "filter_year": "Année",
        "filter_all_years": "Toutes les années",
        "filter_order": "Ordre",
        "order_recent": "Plus récentes",
        "order_oldest": "Plus anciennes",
        "order_title": "A – Z",
        "empty": "Aucune œuvre ne correspond à cette sélection.",
        "empty_reset": "Afficher toutes les œuvres",

        "work_description": "{title}, {medium} sur toile, {year}, {size}. Par Juliana Haggoo.",
        "work_medium": "Technique",
        "work_year": "Année",
        "work_dimensions": "Dimensions",
        "work_status": "Statut",
        "work_on_canvas": "{medium} sur toile",
        "work_enquire": "Se renseigner sur cette œuvre",
        "work_enquiry_subject": "Renseignement — {title} ({year})",
        "work_back": "Retour au portfolio",
        "work_in_situ": "En situation",
        "work_more": "Autres œuvres",
        "work_previous": "Précédente",
        "work_next": "Suivante",
        "work_enlarge": "Agrandir {title}",
        "work_enlarge_view": "Agrandir la vue {n} de {title}",
        "work_view_alt": "{title} — vue {n}",
        "work_alt": "{title} — {medium}, {year}",
        "work_nav": "Œuvres",
        "sold": "Vendu",
        "on_request": "Sur demande",
        "medium_oil": "Huile",
        "medium_acrylic": "Acrylique",
        "painting": "peinture",

        "events_title": "Événements — Juliana Haggoo",
        "events_description": ("Expositions et films de Juliana Haggoo, dont la Noho House Gallery "
                               "de Barcelone, en janvier 2025."),
        "events_heading": "Événements",
        "event_exhibition": "Exposition",
        "event_exhibition_venue": "Noho House Gallery, Barcelone",
        "event_exhibition_date": "23 janvier 2025",
        "event_temptation": "Dark &amp; Light as the love : the Temptation",
        "event_temptation_kind": "Un film",

        "exhibition_title": "Exposition, Barcelone — Juliana Haggoo",
        "exhibition_description": "Exposition — 23 janvier 2025, Noho House Gallery, Barcelone.",
        "exhibition_film_note": "Film du vernissage — lancez la lecture pour le charger.",
        "exhibition_evening": "La soirée",
        "exhibition_photographs": "{n} photographies",
        "exhibition_photo_alt": "Exposition à la Noho House Gallery, Barcelone — photographie {n}",
        "exhibition_enlarge": "Agrandir la photographie {n}",

        "temptation_title": "Dark & Light as the love : the Temptation — Juliana Haggoo",
        "temptation_description": "Dark & Light as the love : the Temptation — un film de Juliana Haggoo.",
        "temptation_heading": "Dark &amp; Light as the love :<br>the Temptation",
        "temptation_note": "Lancez la lecture pour charger le film.",
        "temptation_back": "Retour aux événements",

        "viewer_label": "Visionneuse",
        "viewer_close": "Fermer la visionneuse",
        "viewer_prev": "Image précédente",
        "viewer_next": "Image suivante",
        "viewer_open": "Voir l’œuvre",

        "slider_label": "Juliana Haggoo et son œuvre",
        "slider_prev": "Diapositive précédente",
        "slider_next": "Diapositive suivante",
        "slider_dots": "Choisir une diapositive",
        "slider_goto": "Aller à la diapositive {n}",
        "slider_pause": "Pause",
        "slider_play": "Lecture",
        "slider_pause_label": "Mettre le carrousel en pause",
        "slider_play_label": "Lancer le carrousel",
        "slider_status": "Diapositive {n} sur {total}",
        "slide_monochrome_alt": "Juliana Haggoo à côté d’une toile en noir et blanc",
        "slide_monochrome_caption": "Serenity of Motion",
        "slide_studio_alt": "Juliana Haggoo devant une toile bleue et rouge",
        "slide_studio_caption": "À l’atelier",
    },
}

# The artist's own account, in six steps.
TIMELINE = {
    "en": [
        ("2005", "My artistic journey began when I joined a jazz band in Paris. We shared our "
                 "passion through intimate concerts."),
        ("Then", "I explored a more personal approach, blending singing and dancing in Parisian "
                 "cabarets. However, this hectic pace exhausted me."),
        ("2007", "Painting became my outlet. I immersed myself in abstract art, letting my "
                 "emotions flow onto the canvas."),
        ("At night", "It is at night, with music, that my creativity fully blossoms. Classical "
                     "music and jazz fuel my artistic impulses."),
        ("Mentors", "I discovered contemporary art thanks to benevolent mentors. It allows me to "
                    "explore my emotions and structure them artistically."),
        ("Today", "My journey fuses music, dance and painting. It exemplifies resilience and the "
                  "liberating power of art."),
    ],
    "fr": [
        ("2005", "Mon parcours artistique a commencé lorsque j’ai rejoint un groupe de jazz à "
                 "Paris. Nous partagions notre passion lors de concerts intimes."),
        ("Ensuite", "J’ai exploré une approche plus personnelle, mêlant chant et danse dans les "
                    "cabarets parisiens. Mais ce rythme effréné m’a épuisée."),
        ("2007", "La peinture est devenue mon exutoire. Je me suis plongée dans l’art abstrait, "
                 "laissant mes émotions se déverser sur la toile."),
        ("La nuit", "C’est la nuit, en musique, que ma créativité s’épanouit pleinement. La "
                    "musique classique et le jazz nourrissent mes élans artistiques."),
        ("Mentors", "J’ai découvert l’art contemporain grâce à des mentors bienveillants. Il me "
                    "permet d’explorer mes émotions et de les structurer artistiquement."),
        ("Aujourd’hui", "Mon chemin réunit la musique, la danse et la peinture. Il dit la "
                        "résilience et le pouvoir libérateur de l’art."),
    ],
}


def t(lang: str, key: str, **fields: object) -> str:
    """Look a string up, filling in its placeholders."""
    value = STRINGS[lang][key]
    return value.format(**fields) if fields else value


def medium(lang: str, name: str) -> str:
    """"Oil" and "Acrylic" are catalogue values; the page shows them translated."""
    return STRINGS[lang][f"medium_{name.lower()}"]


def tag(lang: str, work: dict) -> str:
    """The price, or why there isn't one."""
    if work["sold"]:
        return t(lang, "sold")
    return work["price"] or t(lang, "on_request")
