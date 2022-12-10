## Procédure pour permettre la détection du proxy

Pour permettre à notre proxy d'être détecté par notre navigateur, il faut que le navigateur le detecte:

	Sur Firefox

	Paramètres -> (section)Paramètres réseau -> Parmaètres... -> configuration manuelle du proxy
	Mettre 0.0.0.0 et port 80 (cocher pour utiliser ce protocole pour HTTPS)

Puis pour lance le proxy faire dans un terminal

	sudo python3 proxy.py
 

## Commentaire divers des dev
