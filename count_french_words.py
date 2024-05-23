import spacy
import sys
from collections import Counter
from tabulate import tabulate
from spacy.parts_of_speech import PROPN

def is_proper_noun(token):
    if token.doc.is_tagged is False:  # check if the document was POS-tagged
        raise ValueError('token is not POS-tagged')

    return token.pos == PROPN

def compter_mots_francais(fichier):
    # Chargez le modèle de langue française de spaCy
    nlp = spacy.load('fr_core_news_md')

    # Lisez le contenu du fichier
    with open(fichier, 'r', encoding='utf-8') as f:
        texte = f.read()

    nlp.max_length = len(texte) + 100

    # Traitez le texte avec spaCy
    doc = nlp(texte)
    stop_words = nlp.Defaults.stop_words
    # Extraire les mots français (tokens) en ignorant la ponctuation et les espaces
    mots = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ not in stop_words and token.lemma_ and not is_proper_noun(token) ]

    
    # Comptez les mots différents
    return(Counter(mots))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py nom_du_fichier")
        sys.exit(1)

    file_path = sys.argv[1]
    unique_words = compter_mots_francais(file_path)

    # Trier par ordre décroissant d'occurrences
    mots_tries = unique_words.most_common(100)

    # Afficher le tableau formaté
    print(tabulate(mots_tries, headers=["Mot", "Fréquence"], tablefmt="pretty"))
    
    # Affichez le nombre de mots différents
    print(f"Nombre de mots français différents: {len(unique_words)} dans {file_path}")


    
    
    
