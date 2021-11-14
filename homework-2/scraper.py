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
# wordList = words.getWords(10)
wordList = ['景気']
count = 0

# This website gets its information from multiple dictionaries
# These dictionaries give multiple definitions and are placed in containers
# Below is some logic to try to find the container with the most definitions

# Each argument here is a the entire HTML element, not just the text
def definitionField(meaning, sentence, translation):
    if (sentence == None or translation == None):
        return (
            {
                "Meaning": meaning.text,
            })
    
    else:
        return (
            {
                "Meaning": meaning.text,
                "Example": {
                    "Sentence": sentence.text,
                    "Translation": translation.text,
                } 
            })

def grabDefinitions():
    definitions = []
    defs = []
    defs_lens = []
    defs_classes = []
    def_container = None
    def_class = "content-explanation je"

    # Count all definition blocks... This website uses 4 different sources
    # Kejje class can come in two different layouts, Kejje1 and Kejje2
    for i in soup.find_all(class_="Kejje"):
        
        len = i.find_all(class_="level0").__len__()
        if (len == 0):

            continue
        else:
            defs.append(i)
            defs_classes.append("Kejje")

        defs_lens.append(len)

    for i in soup.find_all(class_="Nwnej"):
        defs.append(i)
        defs_lens.append(i.find_all(class_="nwnejT").__len__()) 
        defs_classes.append("Nwnej")

    for i in soup.find_all(class_="hlt_JMDCT"):
        defs.append(i)
        defs_lens.append(i.find_all(class_="jmdctGls").__len__()) 
        defs_classes.append("hlt_JMDCT")

    for i in soup.find_all(class_="Stwdj"):
        defs.append(i)
        # Definition container class : "stwdjNB"
        defs_lens.append( i.find_all(class_="stwdjNB").__len__() ) 
        defs_classes.append("Stwdj")
    
    print( defs_classes, defs_lens )

    # if there are >0 definition blocks, pick the one with the most definitions
    if (defs_lens != [] ):
        best_index = defs_lens.index( max(defs_lens) )
        best_len = defs_lens[best_index]

        # We will now set the container we are looking at to the 
        # dictionary block that contains the most definitions
        def_container = defs[best_index] if best_len>0 else None
        def_class = defs_classes[best_index] if best_len>0 else "content-explanation je"

    # If neither block exists, use the default "content-explanation je" block
    if (def_class == "content-explanation je"):
        
        def_container = soup.find("td", class_="content-explanation je")
        
        # In the rare case that a word is not defined anywhere, return None.
        # In main loop we will check if definitions == None, in that case
        # we will skip the word entirely and move on to the next word.
        if (def_container == None):
            return None

        for str in def_container.text.split('、'):
            definitions.append({"Meaning:": str })

    elif (def_class == "Kejje"):
        # Grab all the definitions from this container
        def_container = def_container.findAll("div", class_="lvlBje")

        for i in range(def_container.__len__()):
            # Grab all the example sentences 
            sentence_jp = def_container[i].findNext(class_="lvlBje")
            sentence_eng = def_container[i].findNext(class_="kenjeEnE")
            
            # Try to find another example sentence
            if ( sentence_jp==None or sentence_eng==None):
                sentence_jp = def_container[i].findNext(class_="KejjeYrJp")
                sentence_eng = def_container[i].findNext(class_="KejjeYrEn")

            # sentences may not exist. Only append to definitions if they exist
            definitions.append( definitionField(
                def_container[i], 
                sentence_jp, 
                sentence_eng)
            )
            
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

            definitions.append( definitionField(
                def_container[i], 
                sentence_jp, 
                sentence_eng)
            )

    elif (def_class == "hlt_JMDCT"):
        def_container = def_container.find_all("div", class_="jmdctGls")

        for i in range(def_container.__len__()):
            def_and_synonyms = def_container[i]\
                .findNext("tr").findNext("tr")\
                .findNext("td").findNext("td")

            definitions.append( 
                definitionField(def_and_synonyms, None, None))

    elif (def_class == "Stwdj"):
        def_container = def_container.find_all("p", class_="stwdjNB")

        for i in range(def_container.__len__()):
            sentence_jp = def_container[i].find_next(class_="stwdjYrJp")
            sentence_eng = def_container[i].find_next(class_="stwdjYrEn")

            definitions.append( definitionField(
                def_container[i],
                sentence_jp,
                sentence_eng
            ))

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
    examples = soup.find_all('div', class_="qotC")
    
    if (examples==None):
        return None

    for i in range(examples.__len__()):
        sentence_jp = examples[i].find('p', class_='qotCJJ')
        sentence_eng = examples[i].find('p', class_='qotCJE')
        
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
    split_kanji = splitter.extract_unicode_block(kanji, w)
    POS = grabPOS()
    reading = grabReading()
    examples = grabExamples()

    # Dont bother adding anything if there is no definition to it
    if (definitions == None):
        continue
    elif (definitions == []):
        print("WTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\n")

    print( '\n\n Word:', w )
    print( "POS:", POS )
    print( 'Kanji:', splitter.extract_unicode_block(kanji, w) )
    print( 'Reading:', reading )
    pprint.pprint( definitions )
    
    # if (examples != None):
    #     pprint.pprint( examples )
