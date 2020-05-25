import random

def findQuotations(listOfParas):

    quotation_paragraphs = []
    for paragraph in listOfParas:
        if 'said' in paragraph and '"' in paragraph:
            quotation_paragraphs.append(paragraph)

    
    return quotation_paragraphs

def produceCloze(listOfParas, quant=3):

    choosing = True
    cloze_ified_paras = []

    while choosing:

        selected_para = random.choice(listOfParas)


        paraList = selected_para.split(' ')
        if len(paraList) < 10:
            continue

        cloze_word_limit = len(paraList) // 3

        indexes_to_replace = random.sample(range(0, len(paraList)-1,), cloze_word_limit)

        # print(indexes_to_replace)

        for i in indexes_to_replace:
            word_to_replace = paraList[i]
            if len(word_to_replace) < 2:
                continue
            cloze_replacement = '__'*len(word_to_replace)
            paraList[i] = cloze_replacement

        cloze_ified_paras.append(' '.join(paraList))

        if len(cloze_ified_paras) >= quant:
            choosing = False

    return cloze_ified_paras



