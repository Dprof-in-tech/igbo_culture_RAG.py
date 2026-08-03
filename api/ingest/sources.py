"""The corpus source registry.

Two kinds of source:

* ``mediawiki`` — fetched as clean plaintext through the MediaWiki API, which
  is far better material than scraping rendered HTML. Titles resolve through
  redirects.
* ``web`` — ordinary pages, fetched and reduced to text.

The English and Igbo Wikipedia titles below were enumerated from Wikipedia's
own Igbo categories and then verified to exist, rather than guessed. Titles
that stop resolving are logged and skipped at fetch time, so a stale entry
costs nothing but a warning.

To grow the corpus, add to the appropriate group. `python3 -m api.ingest
--only <tag>` runs a single group.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Kind = Literal["mediawiki", "web"]


@dataclass(frozen=True)
class Source:
    kind: Kind
    #: Article title for mediawiki sources, full URL for web sources.
    ref: str
    #: Broad area, used for `--only` filtering and stored on every document.
    tag: str
    #: MediaWiki host; ignored for web sources.
    host: str = "en.wikipedia.org"

    @property
    def key(self) -> str:
        if self.kind == "mediawiki":
            return f"{self.kind}:{self.host}:{self.ref}"
        return self.ref


def _wiki(titles: list[str], tag: str, host: str = "en.wikipedia.org") -> list[Source]:
    return [Source("mediawiki", title, tag, host) for title in titles]


def _web(urls: list[str], tag: str) -> list[Source]:
    return [Source("web", url, tag) for url in urls]


# --- People, polity, historical record ---

HISTORY = _wiki(
    [
        "1953 Kano riot",
        "Ahebi Ugbabe",
        "Aro Confederacy",
        "Arochukwu",
        "Biafra",
        "Eze",
        "History of the Aro people",
        "Igbo Americans",
        "Igbo Landing",
        "Igbo apprentice system",
        "Igbo nationalism",
        "Igbo people in the Atlantic slave trade",
        "Igbo-Ukwu",
        "Igboland",
        "Ikwechegh",
        "Jaja of Opobo",
        "Killing of twins in Nigeria",
        "Kingdom of Nri",
        "Nneji (surname)",
        "Nnewi Kingdom",
        "Nri-Igbo",
        "Oke Nnachi",
        "Olukumi people",
        "Timeline of Igbo history",
        "Women's War",
    ],
    "history",
)

# --- Belief, deities, divination, ritual ---

COSMOLOGY = _wiki(
    [
        "Ala (odinani)",
        "Alusi",
        "Amadioha",
        "Anyanwu",
        "Chukwu",
        "Dibịa",
        "Ekpe",
        "Ekwensu",
        "Eri (king)",
        "Ibini Ukpabi",
        "Ibo loa",
        "Ijele Masquerade",
        "Ikenga",
        "Inouwa",
        "Iyi-uwa",
        "Odinani",
        "Ogbanje",
        "Ogu na Ofo",
    ],
    "cosmology",
)

# --- Ceremony, kinship, social order, festivals ---

CUSTOM = _wiki(
    [
        "Afa (Igbo divination)",
        "Age grade",
        "Akupe (hand fan)",
        "Akwa ocha",
        "August meeting",
        "Bride price",
        "Chi (Igbo)",
        "Egedege Dance",
        "Ichi (scarification)",
        "Igbo Yam Festivals",
        "Igbo architecture",
        "Igbo calendar",
        "Igbo culture",
        "Igbo literature",
        "Igbo name",
        "Igbo regalia and headdresses",
        "Igwe",
        "Igwe of Awka-Etiti",
        "Ikeji festival",
        "Imo Awka Festival",
        "Isiagu",
        "Ito Ogbo Festival",
        "Iwa Akwa",
        "Jioji cloth",
        "Kola nut",
        "Masquerade Festival in Igboland",
        "Mbari house",
        "Mbeku",
        "Mmanwu",
        "Nnewi Afiaolu Festival",
        "Nsude pyramid shrines",
        "Oba Ji (Yam barn)",
        "Obi (ruler)",
        "Odogwu",
        "Odunke",
        "Ofala Festival",
        "Ohafia War Dance",
        "Okpu Agu",
        "Okpu Ozo",
        "Okumkpa",
        "Omenuko",
        "Onyishi",
        "Osu caste system",
        "Sam Uzochukwu",
        "Sitting on a man",
        "Traditional marriage in Igbo culture",
        "Ukara cloth",
        "Zanthoxylum gilletii",
        "Ọmụgwọ",
    ],
    "custom",
)

# --- Subgroups, clans, communities ---

SOCIETY = _wiki(
    [
        "1945 Jos riots",
        "1966 anti-Igbo pogrom",
        "Abazu-Akabo",
        "Adamma (masquerade)",
        "Agbogho Mmuo",
        "Akachukwu Sullivan Nwankpo",
        "Anioma Region",
        "Anti-Igbo sentiment",
        "Ariam/Usaka",
        "Biafra Zionist Front",
        "Edda people",
        "Ekwe Community",
        "Ezaa people",
        "Flag of Biafra",
        "Ibere",
        "Igbo Jews",
        "Igbo people",
        "Ikwo people",
        "Isu people",
        "Izzi people",
        "Mgbo people",
        "Ndoki tribe",
        "Ngwa people",
        "Ngwo",
        "Njiko Igbo Movement",
        "Nze na Ozo",
        "Oboro (Nigeria)",
        "Ogba people",
        "Ohaozara people",
        "Ohuhu people",
        "Oloko",
        "Onitsha-Ado",
        "Owo, Enugu State",
        "Umunoha",
        "Umuoji",
        "Umuokpara",
        "Waawa",
        "World Igbo Summit Group",
        "Ọhanaeze Ndigbo",
    ],
    "society",
)

# --- Language, script, names, literature ---

LANGUAGE = _wiki(
    [
        "Acholonu",
        "Akachukwu",
        "Akunna",
        "Alozie",
        "Amaechi",
        "Amuneke",
        "Anyadike",
        "Azikiwe",
        "Chibuzor",
        "Chika (Igbo given name)",
        "Chinenye",
        "Chioma",
        "Chukwuemeka",
        "Ebubechukwu",
        "Ejiogu",
        "Emeghara",
        "Enuani dialect",
        "Enugu (city)",
        "Ezaa language",
        "Ezinne",
        "Ibekwe",
        "Ifeoma",
        "Igbo alphabet",
        "Igbo language",
        "Igboid languages",
        "Ihemelu",
        "Ika language (Nigeria)",
        "Ikechukwu (name)",
        "Ikpeazu",
        "Ikwo language",
        "Izi language",
        "Kanye (name)",
        "Mgbo language",
        "Monye",
        "Ngwa dialect",
        "Nigerian braille",
        "Nkechi",
        "Nkem",
        "Nnamdi",
        "Nsibidi",
        "Ntezi",
        "Ntezi-Aba",
        "Nwachukwu",
        "Nwagu Aneke script",
        "Nwakaeme",
        "Nwodo",
        "Nwokike",
        "Nwokorie",
        "Obasi",
        "Obeah and wanga",
        "Obinna",
        "Obuh",
        "Odita",
        "Ogbodo",
        "Ogbonnaya",
        "Ogbu",
        "Okocha",
        "Okojie",
        "Okonma",
        "Okoro",
        "Okoye",
        "Okpara",
        "Okra",
        "Onyeama",
        "Onyegbule",
        "Onyeka",
        "Onyekachi",
        "Society for Promoting Igbo Language and Culture",
        "Ugochukwu",
        "Ugonna",
    ],
    "language",
)

# --- Art, music, dress, architecture, masquerade ---

ARTS = _wiki(
    [
        "Akwete cloth",
        "Archaeology of Igbo-Ukwu",
        "Atilogwu",
        "Ekpili",
        "Ekwe",
        "Ichaka",
        "Igbo Christian music",
        "Igbo art",
        "Igbo music",
        "Ikechukwu",
        "Ikorodo",
        "Ikwokirikwo",
        "Ka Esi Le Onye Isi Oche",
        "Odumodu music",
        "Ogene",
        "Udu",
        "Uli (design)",
    ],
    "arts",
)

# --- Cuisine and food culture ---

FOOD = _wiki(
    [
        "Abacha (food)",
        "Abula (soup)",
        "Agidi",
        "Akidi",
        "Banga rice",
        "Boli (plantain)",
        "Draw soup",
        "Echicha",
        "Egusi",
        "Egusi sauce",
        "Fio Fio",
        "Fufu",
        "Garri",
        "Igbo cuisine",
        "Isi ewu",
        "Ji akwụkwọ nri",
        "Ji mmiri ọkụ",
        "New Yam Festivals in Nigeria",
        "Nkwobi",
        "Ofe Achara",
        "Ofe Akparata",
        "Ofe Nsala",
        "Ofe Owerri",
        "Ofe Ujuju",
        "Ofe akwụ",
        "Ofe onugbu",
        "Ogbono soup",
        "Okpa",
        "Okra soup",
        "Pounded yam",
        "Ukazi soup",
        "Ukwa (food)",
        "Yam (vegetable)",
        "Ụtara",
    ],
    "food",
)

# --- Igbo writers and their works ---

LETTERS = _wiki(
    [
        "Arrow of God",
        "Buchi Emecheta",
        "Chimamanda Ngozi Adichie",
        "Chinua Achebe",
        "Flora Nwapa",
        "Things Fall Apart",
    ],
    "letters",
)

# --- Igbo-language Wikipedia ---
#
# Written in Igbo, so these passages carry idiom and phrasing the English
# articles cannot. The "Ilu N" pages are proverb collections.

IGBO_WIKI = _wiki(
    [
        "Ilu 1",
        "Ndepụta ememme na Naịjirịa",
        "Ǹsìbìdì",
        "Ọrụ nwoke na nwanyị na ọdịbendị ụmụ amaala Naijiria",
        "Omenala",
        "Ilu 8",
        "Ilu 30",
        "Ilu 6",
        "Ịgụ na ide omenala",
        "Ilu nwanyi na omenala igbo",
        "Ilu igbo",
        "Igbo highlife",
        "Emume Afiaọlụ Nnewi",
        "Mmanwụ",
        "Ndị Ìgbò",
        "Asụsụ Igbo",
        "Ọjị",
    ],
    "igbo-language",
    host="ig.wikipedia.org",
)

# --- Proverb collections ---

PROVERBS = _wiki(["Igbo proverbs"], "proverbs", host="en.wikiquote.org") + _web(
    [
        "https://steemit.com/nigeria/@leopantro/50-igbo-proverbs-and-idioms",
        "https://www.zikoko.com/life/15-igbo-proverbs-and-their-meanings/",
        "https://www.igboguide.org/guests/igbo-proverbs.htm",
        "https://www.igbounionofwashington.com/post/igbo-proverbs-and-their-meanings",
        "https://oiroegbu.com/learn-africa/the-igbo-and-their-proverbs/",
        "https://sloaneangelou.blog/journal/100-igbo-proverbs",
    ],
    "proverbs",
)

# --- Reference and cultural writing ---

REFERENCE = _web(
    [f"https://www.igboguide.org/HT-chapter{n}.htm" for n in range(1, 9)],
    "reference",
)


SOURCES: list[Source] = [
    *HISTORY,
    *COSMOLOGY,
    *CUSTOM,
    *SOCIETY,
    *LANGUAGE,
    *ARTS,
    *FOOD,
    *LETTERS,
    *IGBO_WIKI,
    *PROVERBS,
    *REFERENCE,
]

TAGS = sorted({source.tag for source in SOURCES})
