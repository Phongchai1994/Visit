================================================================================
EPSON Advanced Printer Driver 6 for TM-T82X

                                Copyright (C) 2019 Seiko Epson Corporation
================================================================================

1. À propos de ce logiciel
    Ce pack comprend le logiciel suivant, compatible avec une imprimante EPSON de la série TM.

    1) Pilote d'imprimante Windows
        Ce pilote est un pilote d'imprimante Windows pour l'imprimante TM.
        Il permet d'imprimer depuis une application Windows.

    2) Systèmes d'exploitation pris en charge
        Le pilote est compatible avec les systèmes d'exploitation suivants :

        Windows 11
        Windows 10
        Windows 8.1
        Windows 8
        Windows 7 SP1 (*)
        Windows Server 2025 
        Windows Server 2022 
        Windows Server 2019 
        Windows Server 2016 
        Windows Server 2012 R2 
        Windows Server 2012 
        Windows Server 2008 R2 SP1 
        Windows Server 2008 SP2 
        Windows Embedded 8.1 Industry
        Windows Embedded Standard 7
        Windows Embedded POSReady 7

        * Un message d'avertissement peut s'afficher lors de l'installation du pilote sous Windows 7.
          Ceci ne se produit pas dans un environnement où la dernière mise à jour de sécurité est déployée.

    3) Écrans client pris en charge
        EPSON TM-T82X

        Le pilote fonctionne quelle que soit la version du micrologiciel de l'écran client.

2. Fichiers fournis
   - APD_612_T82X_WM.zip                 : Programme d'installation du pilote d'imprimante avec manuels   
        +--- APD_612_T82X.exe            : Programme d'installation
        +--- APD6_Install_fr_revA.pdf    : Manuel d'installation
        +--- APD6_Printer_fr_revA.pdf    : Manuel de l'imprimante
        +--- APD6_Spec_T82X_fr_revA.pdf  : Spécifications de l'écran client
        +--- README_FR.txt               : Ce document

   Pour installer le pilote d'imprimante, reportez-vous au manuel d'installation.
3. Remarques

    1) Pour des informations détaillées, veuillez consulter chaque manuel.
    2) Si un message d'erreur s'affiche lors de l'installation, la procédure suivante peut permettre de résoudre leproblème.
    	1) Sélectionnez l'option de désinstallation et exécutez le programme d'installation « APD_612_T82X".exe/uninstall ».
    	2) Supprimez le facteur d'erreur.
    	3) Exécutez le programme d'installation « APD_612_T82X.exe ».

    3) Veuillez utiliser la même version du pilote d'imprimante EPSON Advanced pour chaque hôte lorsqu'une imprimante réseau est partagée entre deux hôtes ou plus.

    4) Veuillez installer « StatusAPI pour le pilote d'imprimante EPSON Advanced 6 » si vous souhaitez utiliser « StatusAPI ».

4.Modification de l'ancienne version

    Ver6.12
        - Ajout de la prise en charge de Windows 11 ARM64
        - Prise en charge de la fonctionnalité Smart App Control.
        - Les bugs suivants ont été corrigés.
            - Problème où l'occupation de l'imprimante ne pouvait pas être libérée, ce qui entraînait un blocage de l'impression.
            - L'impression depuis les navigateurs Chrome/Edge pouvait planter.
	

    Ver6.04
        - Les bugs suivants ont été corrigés.
            - Lors de l’impression de caractères demi-chasse avec des polices multilingues, il peut être impossible d’imprimer jusqu’à la largeur maximale.

    Ver6.01 
        - Les bugs suivants ont été corrigés.
            - Une partie de l’interface utilisateur affichée lors de l’installation est illisible.

    Ver6.00
        - Nouvelle version.