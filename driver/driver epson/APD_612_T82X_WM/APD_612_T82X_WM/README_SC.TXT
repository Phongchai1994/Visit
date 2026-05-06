================================================================================
EPSON Advanced Printer Driver 6 for TM-T82X

                                Copyright (C) 2019 Seiko Epson Corporation
================================================================================

1. About this software
    This package includes the following software program to use with an EPSON TM series printer.

    1) Windows Printer Driver
        This driver is a Windows Printer Driver for the TM printer.
        This driver makes it possible to print from a Windows application.

    2) Supported OS
        The driver operation has been supported with the following operating systems. 

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

        * A warning message may be displayed when installing the driver on Windows 7.
          That is not occur in the environment where the latest security update is implemented.

    3) Supported Printers
        EPSON TM-T82X

        The printer driver operates regardless of the pritner firmware version.


2. Supplied Files
    - APD_612_T82X_WM.zip                 : Printer Driver installer with manuals
        +--- APD_612_T82X.exe             : Installer
        +--- APD6_Install_sc_revH.pdf     : Install Manual
        +--- APD6_Printer_sc_revD.pdf     : Printer Manual
        +--- APD6_Spec_T82X_sc_revB.pdf   : Printer Specification
        +--- README_SC.txt                : This document

    How to install the printer driver, refer to the install manual.


3. Remarks
    1) For detailed information, please read each manual.

    2) When an error message is displayed during installation, the following procedure may enable to
       recover from the error.
       1) Specify the uninstall option, and execute the installer "APD_612_T82X.exe /uninstall".
       2) Remove the error factor.
       3) Execute the installer "APD_612_T82X.exe".

    3) Please use the same version of EPSON Advanced Printer Driver for each host when a network printer
       is shared among two or more hosts.

    4) Please install "StatusAPI for EPSON Advanced Printer Driver 6", if you would like to use "StatusAPI".


4.Modification from the old version

    Ver6.12
       - Added support for Windows 11 ARM64.
       - Supported the Smart App Control feature.
       - Added support for models that comply with the UK's PSTI bill.          
       - The following bugs have been fixed.
           - The Issue where printer occupancy could not be released, causing printing to stall.
           - Printing from Chrome/Edge browsers may crash.

    Ver6.04
        - The following bugs have been fixed.
            - When printing half-width characters with multilingual fonts, it may not be possible to
              print up to the maximum print width.

    Ver6.01
        - The following bugs have been fixed.
            - Part of UI displayed during installation is garbled.

    Ver6.00
        - New release.
