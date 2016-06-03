
# PICBOT bot for slack 

## Introduction
Ce bot permet d'upload dans slack des images random du site xkcd.com.

## Fonctionnalités
* il suffit d’inclure le bot à la conversation puis de l’appeler en tapant @pictbot:
suivie d’une de ces 4 commande :

"pic"
"picture"
"joke"
"help"

* picture ou pic (raccourci pour l’utilisateur), renvoie dans le chat une image aléatoire issue de xkcd.com.
* joke, renvoie dans le chat une petite blague de programmeur
* help, renvoie dans le chat un message d'aide contenant les différentes commandes.

## Installation

### LINUX based

* $ python3 -m venv slack
* $ cd slack
* $ git clone https://github.com/cyrilmanuel/picbot
* $ . bin/activate
* (slack)$ cd picbot //do this twice, because reasons
* (slack)$ pip install -e .

* (slack)$ export TOKEN=xoxb-123 //this token is given to you by slack.
* (slack)$ python -m picbot

### WINDOWS based

* > python -m venv slack
* > cd slack
* $ git clone https://github.com/cyrilmanuel/picbot
* > Scripts\activate.bat
* (slack)> cd picbot  //do this twice, because reasons
* (slack)> pip install -e .

* (slack)> set TOKEN=xoxb-123 //this token is given to you by slack.
* (slack)> python -m picbot

