from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import sys
import re
import unidecode
import os

def generer_variantes_nom(president):
    # Générer les variantes du nom du président
    parties = president.split()
    
    initiales = "".join([p[0] for p in parties])
    initiales_avec_points = ".".join(initiales) + "."
    initiale_du_prenom_et_nom = initiales[0]+". "+" ".join(parties[1:]) # Retirer le premier mot
    
    variantes = {
        president.lower(),
        re.sub("'", "’", president.lower()),
        initiales.lower(),
        initiales_avec_points.lower(),
        initiale_du_prenom_et_nom.lower(),
        re.sub("'", "’", initiale_du_prenom_et_nom.lower()),
        "r",
        "le president",
        "le président"
    }
    
    return variantes

def identifier_orateurs(texte):
    # Regex pour trouver les orateurs selon les différents formats
    pattern = re.compile(r"^((?:M(?:r|rs|me)?\.?\s+)?[A-Z][A-Za-zÀ-ÖØ-öø-ÿ\-'’.]*(?:\s[1A-Za-z][A-Za-zÀ-ÖØ-öø-ÿ'’.]*){0,3})(?=\s-|\s*:|\s*$)", re.MULTILINE)    
    orateurs = set(pattern.findall(texte))
    return sorted(orateurs)

def ligne_commence_par_mot(ligne, mots):
    ligne = ligne.strip().lower()
    for mot in mots:
        if not ligne.startswith(mot.lower()):
            continue
        suffixe = ligne[len(mot):].strip()  # Extraire le suffixe après la phrase cible
        if any(suffixe.startswith(s) for s in [":", "-", "--"]) or not suffixe :
            return mot
    return False

def enlever_lignes(texte, mots,president_lower):
    texte = re.sub("\x97", "-", texte)
    texte = re.sub("\x92", "'", texte)
    orateurs = identifier_orateurs(texte)
    print(f"orateurs={orateurs}")

    orateurs.append("q") #pour question
    orateurs.append("question")
    
    # Générer les variantes du nom du président à exclure
    variantes_president = generer_variantes_nom(president)
    
    # Filtrer les orateurs pour exclure le président
    orateur_president = [orateur.lower() for orateur in orateurs if orateur.lower() in variantes_president]

    if (len(orateur_president)==0): #si president n'est pas dans les orateurs, on prend tout le texte
        return texte
    orateurs = [orateur.lower() for orateur in orateurs if orateur.lower() not in variantes_president] #enlever le president des orateurs
    # Diviser le texte en lignes
    lignes = texte.split('\n')
    orateur_courant_president = True
    texte_filtre=""
    for ligne in lignes :
        if ligne_commence_par_mot(ligne,orateurs):
            orateur_courant_president = False
        elif ligne_commence_par_mot(ligne,variantes_president) :
            orateur_courant_president = True
        if orateur_courant_president and not(ligne.strip().endswith('?')) and '---' not in ligne and not any(mot in ligne[:100].lower() for mot in mots):
            texte_filtre += ('\n'+ligne)
  
    return texte_filtre



def scrap_discours(president,taille_max):
    # Configurer les options de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Exécute Chrome en mode headless (sans interface graphique)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Indiquer le chemin vers chromedriver
    chromedriver_path = '/Applications/chromedriver'  # Remplacez par le chemin de votre chromedriver

    # Initialiser le service ChromeDriver
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver2 = webdriver.Chrome(service=service, options=chrome_options)
    # URL de la page de recherche des discours de Nicolas Sarkozy
    base_url = "https://www.vie-publique.fr/discours/recherche?search_api_fulltext_discours=&sort_by=field_date_prononciation_discour&field_intervenant_title="+president+"&field_intervenant_qualite=&field_date_prononciation_discour_interval%5Bmin%5D=&field_date_prononciation_discour_interval%5Bmax%5D=&field_type_de_document%5B9350%5D=9350&field_type_de_document%5B9351%5D=9351&field_type_de_document%5B9353%5D=9353&page="

    # Initialiser le numéro de page
    page_number = 1

    file_size=0

    # Créer un dossier pour enregistrer les fichiers
    os.makedirs('results', exist_ok=True)

    # Initialiser un compteur de discours
    discourse_counter = 1
    nom_famille_president = president.split()[-1].lower()
    

    # Sauvegarder le discours dans un fichier
    with open(f"results/"+president+".txt", "w", encoding='utf-8') as file:
        
            
        while True:
            # Construire l'URL de la page actuelle
            url = f"{base_url}{page_number}"
            print(f"Fetching page: {page_number}")
            # Naviguer vers l'URL
            driver.get(url)
            # time.sleep(1)  # Attendre que la page se charge complètement

            # Créer un répertoire pour stocker les fichiers si ce n'est pas déjà fait
            if not os.path.exists("results"):
                os.makedirs("results")
            try : 
                # Extraire les résultats
                results = driver.find_elements(By.CLASS_NAME, 'fr-card__title')

                if not results :
                    print("No more results found.")
                    break
                if file_size > taille_max:
                    print("Taille max atteinte.")
                    break

                # Itérer sur les résultats et extraire les informations nécessaires
                for index, result in enumerate(results):
                    try:
                        # Extraire les informations pertinentes (par exemple, les liens et les titres)
                        link = result.find_element(By.TAG_NAME, 'a').get_attribute('href')
                        
                        # Naviguer vers le lien du discours
                        driver2.get(link)
                        # time.sleep(1)  # Attendre que la page se charge complètement
                        try:
                            try:
                                title = driver2.find_element(By.CSS_SELECTOR, 'h1.fr-h3').text
                            except NoSuchElementException:
                                title=""
                            intervenants = driver2.find_elements(By.CSS_SELECTOR, 'ul.line-intervenant > li')
                            intervenants_text=""
                            noms_a_supprimer = []
                            for intervenant in intervenants:
                                if (len(intervenant.text)>0):
                                    intervenant_text = intervenant.text.split('-')[0].strip()
                                    intervenant_text = re.sub(r'[^\w\s]', '', intervenant_text) 
                                    nom_famille = intervenant_text.split()[-1].lower()
                                    initiales = intervenant_text.split()[0][0].lower()+"."+nom_famille[0].lower()+"."
                                    if (nom_famille!=nom_famille_president): 
                                        noms_a_supprimer.append(nom_famille)
                                        noms_a_supprimer.append(initiales)
                                    intervenants_text += intervenant_text+"- "
                                        
                            # Trouver le contenu du discours - adapter cette ligne en fonction de la structure HTML actuelle
                            speech_content_element = driver2.find_element(By.CLASS_NAME, 'vp-discours-content')

                            speech_content = speech_content_element.find_element(By.CLASS_NAME, 'field--name-field-texte-integral').text
                            sppech_content_stripped = enlever_lignes(speech_content,noms_a_supprimer,president.lower())
                            
                            file.write(f"\n---Texte # {discourse_counter} Length {len(speech_content)} {len(sppech_content_stripped)} file_size={file_size} {title}\n")                                
                            
                            file.write(sppech_content_stripped)
                            file_size = os.path.getsize("results/"+president+".txt")
                            print(f"Texte # {discourse_counter} Length {len(speech_content)} {len(sppech_content_stripped)} file_size={file_size} link={link}")            
                            print(f"Intervenants ={intervenants_text}\n")
                            if file_size> taille_max:
                                break
                        except NoSuchElementException:
                            print(f"Aucun contenu trouvé pour le discours # {discourse_counter}")
                    except NoSuchElementException:
                        print("Impossible de trouver les informations pour un résultat")
                    
                    discourse_counter += 1
            except NoSuchElementException:
                print("Impossible de trouver les résultats de la recherche")
            
            # Passer à la page suivante
            page_number += 1

    # Fermer le navigateur
    driver.quit()
    driver2.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scrap_discours.py <nom intervenant> <taille max fichier>")
        sys.exit(1)

    president = sys.argv[1]
    taille_max = sys.argv[2]
    scrap_discours(president,int(taille_max))



