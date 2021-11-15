def getWords(lim):
    words = []
    f = open('jp-corpus.txt', 'r', encoding="utf8")
    lines = f.readlines()
    count = 0

    for w in lines:
        if (count > lim):
            break;
        words.append(w[:-1])
        count += 1
    
    return words
