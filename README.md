# Projet de proxy pour Protocole et Programmation Réseau
Ce projet est un proxy qui permet de filtrer les pages web, utilisant le protocole HTTP, de certains mots.
Il a été réalisé par:
- Auberval Florian
- Behuet Timothée
- Siaudeau Romain

---

## Procédure pour permettre la détection du proxy

Pour permettre à notre proxy d'être détecté par notre navigateur, il faut que le navigateur le détecte:

### Sur Firefox

> Paramètres -> (section)Paramètres réseau -> Parmaètres... -> configuration manuelle du proxy
> Mettre 127.0.0.1 et port 8000 (cocher pour utiliser ce protocole pour HTTPS)

Puis pour lancer le proxy faire dans un terminal
```sh
python3 proxy.py
```
## Configuration 
Une fois lancé, le proxy est configurable depuis le site http://config-proxy .
Une fois sur cette page, il est possible d'activer ou désactiver le filtre du proxy. De plus, il est aussi possible de modifier la liste des mots que l'on souhaite bannir, via un textarea. Les différents mots ou sections à bannir doivent être séparé par une nouvelle ligne.
La configuration s'enregistrera dans le fichier wordsBlackList.txt, pour le prochain redémarage du proxy.

## Remarque 
Firefox cache les pages web, ce qui pose encore certain problème:
