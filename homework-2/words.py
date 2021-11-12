
def getWords(count):
    words = []
    f = open('jp-corpus.txt', 'r', encoding="utf8")
    lines = f.readlines()

    lim = count
    for w in lines:
        if (lim>count):
            break;
        words.append(w[:-1])
        count += 1
    
    return words
