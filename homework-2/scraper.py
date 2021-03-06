import requests
from bs4 import BeautifulSoup
import splitter
import words
from pprint import pprint
from pymongo import MongoClient

# Regex expression to split japanese words
hiragana_full = r'[ぁ-ゟ]'
katakana_full = r'[゠-ヿ]'
kanji = r'[㐀-䶵一-鿋豈-頻]'
radicals = r'[⺀-⿕]'
katakana_half_width = r'[｟-ﾟ]'
alphanum_full = r'[！-～]'
symbols_punct = r'[、-〿]'
misc_symbols = r'[ㇰ-ㇿ㈠-㉃㊀-㋾㌀-㍿]'
ascii_char = r'[ -~]'

valid_POS = {
    "名詞": True,
    "固有名詞": True,
    "形式名詞": True,
    "動詞": True,
    "助動詞": True,
    "複合動詞": True,
    "形容動詞": True,
    "連体詞": True,
    "前置詞": True,
    "助数詞": True,
    "否定": True,
    "敬語": True,
    "副助詞": True,
}

ENG_URL = "https://ejje.weblio.jp/content/"
# word = "ブンデスリーガ" 
# wordList = ['M']

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
            reading = reading.findNext("a").findNext("a").text
    
    return reading

def grabPOS():
    POS_list = []
    POS_containers = soup.findAll(class_="jmdctT")
    if(POS_containers == None):
        print("NO POS CONTAINERS!!!")

    for container in POS_containers:
        container = container.findNext("td")
        for POS in container.findChildren("a"):

            if(POS==None):
                print("WTF??")

            if POS.text in valid_POS:
                POS_list.append(POS.text)

    return POS_list

def grabExamples():
    example_sens = []
    examples = soup.find_all('div', class_="qotC")
    
    if (examples==None):
        return None

    for i in range(examples.__len__()):
        # JP --> ENG 
        source = examples[i].find('p', class_='qotCJJ')
        target = examples[i].find('p', class_='qotCJE')

        # ENG --> JP
        if (source == None):
            target = examples[i].find('p', class_='qotCJ')
            source = examples[i].find('p', class_='qotCE')

        if(source==None or target==None):
            continue
        
        # Clean up extraction
        for child in source.find_all(class_=["addToSlBtnCntner", "squareCircle", "fa"]):
            child.decompose()

        for child in target.find_all(["b", "i", "span"]):
            child.decompose()

        example_sens.append({
            'Sentence': source.text, 
            'Translation': target.text
        })

    return example_sens

if __name__ == "__main__":
    wordList = words.getWords(1000)
    # wordList = ["基地"]
    count = 0
    client = MongoClient( #dasdfasdfasdfasdf# )
    db = client.hw2


    for w in wordList:
        print(count)
        print(w)
        count+=1

        page = requests.get( ENG_URL + w )
        soup = BeautifulSoup(page.content, "html.parser")

        definitions = grabDefinitions()
        # If no definitions are found, go to next word.
        if (definitions == None) : 
            continue

        split_kanji = splitter.extract_unicode_block(kanji, w)
        POS = grabPOS()
        reading = grabReading()
        examples = grabExamples()

        entry = {}
        entry['word'] = w
        if (POS!=None): entry['pos'] = POS
        if (reading!=None): entry["reading"] = reading
        if (split_kanji != []): entry["kanji"] = split_kanji
        if (definitions != None): 
            entry["definitions"] = definitions
        if (examples != None): entry["examples"] = examples
        
        result = db.dictionary.insert_one(entry)
        # pprint(result)
        


        # if (definitions == None):
        #     continue
        # elif (definitions == []):
        #     print("WTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\nWTF?\n")

        # print( '\nWord:', w )
        # print( "POS:", POS )
        # print( 'Kanji:', splitter.extract_unicode_block(kanji, w) )
        # print( 'Reading:', reading )

        # pprint( definitions )
        
        # if (examples != None):
        #     pprint( examples )
