# Projet de proxy pour Protocole et Programmation Réseau
Ce projet est un proxy qui permet de filtrer les pages web, utilisant le protocole HTTP, de certains mots.
Il a été réalisé par:
- Auberval Florian
- Behuet Timothée
- Siaudeau Romain

[Dépot github du projet](https://github.com/Me-k-01/Protocoles_et_Programmation_Reseau)

---

## Procédure permettant la détection du proxy

Pour permettre à notre proxy d'être utilisé par notre navigateur, il faut qu'il soit bien configuré:

### Sur Firefox

> Paramètres -> (section)Paramètres réseau -> Parmaètres... -> configuration manuelle du proxy
> Mettre 127.0.0.1 et port 8000 (cocher pour utiliser ce protocole pour HTTPS)

Puis pour lancer le proxy faire dans un terminal
```sh
python3 proxy.py
```

## Configuration 
Une fois lancé, le proxy est configurable depuis l'adresse http://config-proxy .
Une fois sur cette page, il est possible d'activer ou désactiver le filtre du proxy. De plus, il est aussi possible de modifier la liste des mots que l'on souhaite bannir, via un textarea. Les différents mots ou sections à bannir doivent être séparé par une nouvelle ligne.
La configuration s'enregistrera dans le fichier wordsBlackList.txt, pour le prochain redémarage du proxy.

## Remarques 
Firefox cache les pages web, ce qui pose encore certains problèmes de non prise en compte de la nouvelle censure.
Le proxy actuellement fonctionne uniquement avec les connections http. 
Il peut y avoir parfois une erreur de décodage d'un octet lorsque le proxy reçoit une requête. Il faut dans ce cas relancer le programe.

---

## Exemple d'utilisation
### Rendu du configurateur:
![configurateur](https://media.discordapp.net/attachments/1047081966962475028/1055091157438312488/image.png?width=1774&height=1124)
### Valeur du document texte de mémorisation de la configuration:
![blacklist.txt](https://media.discordapp.net/attachments/1047081966962475028/1055093565614739456/image.png)
### Rendu d'un site web avec le proxy actif:
![Exemple de rendu du site p-fb.net](https://media.discordapp.net/attachments/1047081966962475028/1055091766883274762/image.png?width=1776&height=1124)

