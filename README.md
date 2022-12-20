## Procédure pour permettre la détection du proxy

Pour permettre à notre proxy d'être détecté par notre navigateur, il faut que le navigateur le détecte:

	Sur Firefox

	Paramètres -> (section)Paramètres réseau -> Parmaètres... -> configuration manuelle du proxy
	Mettre 127.0.0.1 et port 8000 (cocher pour utiliser ce protocole pour HTTPS)

Puis pour lancer le proxy faire dans un terminal

	python3 proxy.py
 

