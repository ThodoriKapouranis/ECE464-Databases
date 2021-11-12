import requests
from bs4 import BeautifulSoup
import splitter
import words
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
word = "ブンデスリーガ" 
wordList = words.getWords(10)
count = 0
# This website gets its information from multiple dictionaries
# These dictionaries give multiple definitions and are placed in containers
# Below is some logic to try to find the container with the most definitions
def grabDefinitions():
    definitions = []
    defs = []
    defs_lens = []
    defs_classes = []
    def_container = None
    def_class = "content-explanation je"

    for i in soup.find_all(class_="Kejje"):
        defs.append(i)
        len = i.find_all(class_="level0").__len__()
        
        if (len == 0):
            len = i.find_all(class_="level1").__len__()
            
        defs_lens.append(len)
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
    print(defs_classes)
    print(defs_lens)
    print(def_class)
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
            
            # Try to find another example sentence
            if ( sentence_jp==None or sentence_eng==None):
                sentence_jp = def_container[i].findNext(class_="KejjeYrJp")
                sentence_eng = def_container[i].findNext(class_="KejjeYrEn")


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
            
            # Check if we accidentally took another definition's sentence
            if ( i<def_container.__len__()-1 and \
                sentence_jp == def_container[i+1].findNext(class_="nwnejYrJ")
            ):
                sentence_jp = None

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
    
    return definitions

# Some pages do not have reading on top of the words for some reason
def grabReading():
    reading = soup.find("sup", class_="ruby" )
    
    if ( reading!=None ): reading = reading.text

    else:
        # Attempt to get reading from JMdict definition
        # <a> "Reading:" </a> <a> {Reading} </a>
        reading = soup.find("p", class_="jmdctYm")
        if (reading==None):
            reading = ""
        else:
            reading = reading.findNext("a").findNext("a")
    
    return reading

def grabPOS():
    POS = soup.find(class_="stwdjS")
    POS = POS.text if POS!=None else ""
    return POS

def grabExamples():
    example_sens = []
    examples = soup.find_all(class_="qotC")

    for i in range(examples.__len__()):
        sentence_jp = examples[i].find(class_='qotCJJ')
        sentence_eng = examples[i].find(class_='qotCJE')
        
        # Clean up extraction
        for child in sentence_jp.find_all(class_="addToSlBtnCntner"):
            child.decompose()

        for child in sentence_eng.find_all(["b", "i", "span"]):
            child.decompose()

        example_sens.append({
            'Sentence': sentence_jp.text, 
            'Translation': sentence_eng.text
        })

        return example_sens

for w in wordList:
    print(count)
    print(w)
    count+=1

    page = requests.get( ENG_URL + w )
    soup = BeautifulSoup(page.content, "html.parser")

    definitions = grabDefinitions()
    # kanji = splitter.extract_unicode_block(kanji, w)
    POS = grabPOS()
    reading = grabReading()
    examples = grabExamples()


# print( 'Word:', word )
# print( "POS:", POS )
# print( 'Kanji:', splitter.extract_unicode_block(kanji, word) )
# print( 'Reading:', reading )
# pprint.pprint( definitions )
# pprint.pprint( examples_sen )