import requests
from bs4 import BeautifulSoup
import splitter
import pprint

hiragana_full = r'[ぁ-ゟ]'
katakana_full = r'[゠-ヿ]'
kanji = r'[㐀-䶵一-鿋豈-頻]'
radicals = r'[⺀-⿕]'
katakana_half_width = r'[｟-ﾟ]'
alphanum_full = r'[！-～]'
symbols_punct = r'[、-〿]'
misc_symbols = r'[ㇰ-ㇿ㈠-㉃㊀-㋾㌀-㍿]'
ascii_char = r'[ -~]'

ENG_URL = "https://ejje.weblio.jp/content/"
SENTENCE_URL = "https://ejje.weblio.jp/sentence/content/"
word = "薨去" 

page = requests.get( ENG_URL + word )
soup = BeautifulSoup(page.content, "html.parser")

reading = soup.find("sup", class_="ruby" )
definitions = []

# This website gets its information from multiple dictionaries
# These dictionaries give multiple definitions and are placed in containers
# Below is some logic to try to find the container with the most definitions
defs = []
defs_lens = []
defs_classes = []
def_container = None
def_class = "content-explanation je"

for i in soup.find_all(class_="Kejje"):
    defs.append(i)
    defs_lens.append(i.find_all(class_="level0").__len__()) 
    defs_classes.append("Kejje")

for i in soup.find_all(class_="Nwnej"):
    defs.append(i)
    defs_lens.append(i.find_all(class_="nwnejT").__len__()) 
    defs_classes.append("Nwnej")

if (defs_lens != [] ):
    best_index = defs_lens.index( max(defs_lens) )
    best_len = defs_lens[best_index]
    def_container = defs[best_index] if best_len>0 else None
    def_class = defs_classes[best_index] if best_len>0 else "content-explanation je"

# If neither block exists, use the default "content-explanation je" block
if (def_class == "content-explanation je"):
    def_container = soup.find("td", class_="content-explanation je")
    for str in def_container.text.split('、'):
        definitions.append({"Meaning:": str })

elif (def_class == "Kejje"):
    # Grab all the definitions from this container
    def_container = def_container.findAll("div", class_="level0")

    for i in range(def_container.__len__()):
        # Grab all the example sentences 
        sentence_jp = def_container[i].findNext(class_="lvlBje")
        sentence_eng = def_container[i].findNext(class_="kenjeEnE")
        
        # sentences may not exist. Only append to definitions if they exist
        if ( sentence_jp != None and sentence_eng != None ):
            definitions.append({
                "Meaning": def_container[i].text,
                "Example": {
                    "Sentence": sentence_jp.text,
                    "Translation": sentence_eng.text,
                } 
            })
        else: 
            definitions.append({"Definition": def_container[i].text})

elif (def_class == "Nwnej"):
    def_container = def_container.findAll("div", class_="nwnejT")
    
    for i in range(def_container.__len__()):
        sentence_jp = def_container[i].findNext(class_="nwnejYrJ")
        sentence_eng = def_container[i].findNext(class_="nwnejYrE")

        # sentences may not exist. Only append to definitions if they exist
        if ( sentence_jp != None and sentence_eng != None ):
            definitions.append({
                "Meaning": def_container[i].text,
                "Example": {
                    "Sentence": sentence_jp.text,
                    "Translation": sentence_eng.text,
                } 
            })
        else: 
            definitions.append({"Definition": def_container[i].text})

# Some pages do not have reading on top of the words for some reason
if (reading == None):
    # Attempt to get reading from JMdict definition
    # <a> "Reading:" </a> <a> {Reading} </a>
    reading = soup.find("p", class_="jmdctYm").findNext("a").findNext("a")


print( 'Word:', word )
print( "POS:", soup.find(class_="stwdjS").text )
print( 'Kanji:', splitter.extract_unicode_block(kanji, word) )
print( 'Reading:', reading.contents[0] )

pprint.pprint( definitions )

