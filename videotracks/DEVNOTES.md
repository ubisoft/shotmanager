

UAS Shot Manager Dev Notes
-------------------------------------------------------------

# Notes pour doc:
-----------------


# Comportements "spéciaux" ou prod spécifiques:
-----------------------------------------------

* Mettre les propriétés projet en Window global dans le fichier

* Ne supporte pas les camera bindés aux marqueurs
* Pas de notion de séquence
* Utilisation du nom de la scene comme mot clé pour le prefix des sorties (utiliser préfixe projet ou nom de la take?)
* nom de la take principale, Main Take, hardcodé pour ne pas etre enlevé

* Confo:
    - change la couleur des shots
    - nomme les shots retirées en "_remove"


# Notes pour refactoring:
-------------------------

* des valeurs de résolutions hardcodées (1280, 960, 720)
* des chemins hardcodés
* des scripts prod specifique, commençant en général par "RRS"




