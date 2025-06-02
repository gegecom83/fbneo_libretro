# FinalBurn Neo [Libretro] User Manual

## English Version

### Introduction
FinalBurn Neo [Libretro] is a GUI application designed to manage and launch ROMs from the RetroArch emulator with the FinalBurn Neo core. It supports multiple gaming platforms, organized into tabs, and allows joystick navigation, ROM title extraction, and customizable settings.

### System Requirements
- **Operating System**: Windows
- **Dependencies**: RetroArch installed with the FinalBurn Neo core (`fbneo_libretro.dll`)
- **Hardware**: Optional joystick (e.g., Xbox 360 controller) for navigation
- **ROM Files**: ROMs in `.zip`, `.7z`, or `.cue` formats
- **Optional**: XML/DAT files for ROM title extraction

### Installation
1. **Download and Install RetroArch**:
   - Download RetroArch from the official website and install it.
   - Ensure the FinalBurn Neo core (`fbneo_libretro.dll`) is installed in the RetroArch `cores` directory.
2. **Place the Application**:
   - Extract or place the FinalBurn Neo [Libretro] executable or script in a directory of your choice.
   - Ensure the `config.json` file is writable in the same directory.
3. **Prepare ROMs**:
   - Organize your ROM files in directories corresponding to each supported platform (e.g., Arcade, NES, etc.).
   - Optionally, prepare XML/DAT files for ROM title metadata.

### Features
- **Multi-Platform Support**: 17 tabs for different gaming systems (e.g., Arcade, NES, Sega Megadrive, etc.).
- **Joystick Navigation**: Supports joystick input for browsing and launching ROMs.
- **ROM Title Extraction**: Generate ROM title files from XML/DAT files or directory scans.
- **Search Functionality**: Filter ROMs by name within each tab.
- **Fullscreen Mode**: Toggle between windowed and fullscreen modes.
- **Customizable Settings**: Configure RetroArch paths, ROM directories, and joystick controls.

### Usage Instructions

#### Launching the Application
1. Run the `fbneo_libretro.py` script or executable.
2. The GUI will open, displaying the first tab (Arcade) by default.

#### Navigating the Interface
- **Tabs**: Use the dropdown menu or joystick (buttons configured as `Previous Tab` and `Next Tab`) to switch between platforms.
- **ROM List**:
  - View the list of ROMs in the current tab.
  - Use the search bar to filter ROMs by name.
  - Scroll using the mouse, keyboard (up/down arrows), or joystick.
- **Launching a ROM**:
  - Double-click a ROM in the list or select it and press `Enter`.
  - Alternatively, use the joystick's `Select` button (default: button 0).
- **Fullscreen Mode**:
  - Press `F11` to toggle between fullscreen and windowed modes.

#### Configuring Settings
1. Click the **Settings** button in any tab or use the joystick's `Settings` button (default: button 7).
2. In the Settings window:
   - **RetroArch Executable**: Browse to select the `retroarch.exe` file.
   - **RetroArch Core**: Browse to select the `fbneo_libretro.dll` file.
   - **Update All ROMs**: Generate or update ROM title files for all tabs.
   - **Joystick Settings**: Open a sub-window to configure joystick controls.
   - **Generate ROM Titles**: Open a sub-window to extract ROM titles for the current tab.
3. Save changes or restore defaults as needed.

#### Configuring Joystick Controls
1. In the Settings window, click **Joystick Settings**.
2. Adjust the following:
   - **Joystick Y-Axis Index**: Set the axis for vertical navigation (-1 to disable).
   - **Fast Scroll Cooldown**: Time between scroll actions (0.02–0.2 seconds).
   - **Fast Scroll Initial Steps**: Number of items to skip during fast scrolling (1–15).
   - **Button Indices**: Assign buttons for up, down, select, settings, previous tab, and next tab.
3. Use the **Test Joystick** button to verify joystick inputs.
4. Save or restore default settings.

#### Generating ROM Titles
1. In the Settings window, click **Generate ROM Titles**.
2. In the ROM Titles Extractor window:
   - **ROMs Directory**: Select the directory containing ROM files.
   - **Input XML File (Optional)**: Select an XML/DAT file for metadata extraction.
   - **Output Directory**: The default output directory is the application’s directory.
   - **Output File Name**: The default is the tab’s corresponding ROM titles file (e.g., `rom_titles_arcade.txt`).
3. Click **Extract Titles** to generate the ROM titles file.
4. The ROM list in the corresponding tab will update automatically.

#### Updating All ROMs
1. In the Settings window, click **Update All ROMs**.
2. The application will generate or update ROM title files for all tabs based on their configured ROM directories and XML files.
3. A success message lists updated tabs, and warnings are shown for any errors.

### Troubleshooting
- **Error: "Invalid RetroArch executable"**:
  - Ensure the path to `retroarch.exe` is correct in the Settings window.
- **Error: "ROM file not found"**:
  - Verify that the ROMs directory is set correctly and contains `.zip`, `.7z`, or `.cue` files.
- **Joystick Not Detected**:
  - Ensure the joystick is connected before launching the application.
  - Use the **Test Joystick** feature to debug.
- **Permission Denied Errors**:
  - Run the application as an administrator to ensure write access to the `config.json` file and output directories.
- **No ROMs Found**:
  - Check that the ROMs directory is correctly set and contains valid ROM files.

### Support
For issues or inquiries, contact: gegecom83@gmail.com

---

## Version Française

### Introduction
FinalBurn Neo [Libretro] est une application avec une interface graphique conçue pour gérer et lancer des ROMs depuis l'émulateur RetroArch avec le cœur FinalBurn Neo. Elle prend en charge plusieurs plateformes de jeu, organisées en onglets, et permet une navigation par joystick, l'extraction de titres de ROMs, et des paramètres personnalisables.

### Configuration Requise
- **Système d'exploitation** : Windows
- **Dépendances** : RetroArch installé avec le cœur FinalBurn Neo (`fbneo_libretro.dll`)
- **Matériel** : Joystick optionnel (par exemple, manette Xbox 360) pour la navigation
- **Fichiers ROM** : ROMs aux formats `.zip`, `.7z`, ou `.cue`
- **Optionnel** : Fichiers XML/DAT pour l'extraction des métadonnées des ROMs

### Installation
1. **Téléchargez et installez RetroArch** :
   - Téléchargez RetroArch depuis le site officiel et installez-le.
   - Assurez-vous que le cœur FinalBurn Neo (`fbneo_libretro.dll`) est installé dans le répertoire `cores` de RetroArch.
2. **Placez l'application** :
   - Extrayez ou placez l'exécutable ou le script FinalBurn Neo [Libretro] dans un répertoire de votre choix.
   - Assurez-vous que le fichier `config.json` est accessible en écriture dans le même répertoire.
3. **Préparez les ROMs** :
   - Organisez vos fichiers ROM dans des répertoires correspondant à chaque plateforme prise en charge (par exemple, Arcade, NES, etc.).
   - Préparez éventuellement des fichiers XML/DAT pour les métadonnées des titres de ROM.

### Fonctionnalités
- **Support multi-plateforme** : 17 onglets pour différentes plateformes de jeu (par exemple, Arcade, NES, Sega Megadrive, etc.).
- **Navigation par joystick** : Prise en charge des entrées de joystick pour naviguer et lancer des ROMs.
- **Extraction des titres de ROM** : Génération de fichiers de titres de ROM à partir de fichiers XML/DAT ou d'une analyse de répertoires.
- **Fonction de recherche** : Filtrer les ROMs par nom dans chaque onglet.
- **Mode plein écran** : Basculer entre les modes fenêtré et plein écran.
- **Paramètres personnalisables** : Configurer les chemins RetroArch, les répertoires de ROMs, et les contrôles du joystick.

### Instructions d'Utilisation

#### Lancement de l'Application
1. Exécutez le script `fbneo_libretro.py` ou l'exécutable.
2. L'interface graphique s'ouvre, affichant l'onglet Arcade par défaut.

#### Navigation dans l'Interface
- **Onglets** : Utilisez le menu déroulant ou le joystick (boutons configurés comme `Onglet Précédent` et `Onglet Suivant`) pour changer de plateforme.
- **Liste des ROMs** :
  - Affichez la liste des ROMs dans l'onglet actif.
  - Utilisez la barre de recherche pour filtrer les ROMs par nom.
  - Faites défiler avec la souris, le clavier (flèches haut/bas), ou le joystick.
- **Lancer une ROM** :
  - Double-cliquez sur une ROM dans la liste ou sélectionnez-la et appuyez sur `Entrée`.
  - Alternativement, utilisez le bouton `Sélectionner` du joystick (par défaut : bouton 0).
- **Mode Plein Écran** :
  - Appuyez sur `F11` pour basculer entre les modes plein écran et fenêtré.

#### Configuration des Paramètres
1. Cliquez sur le bouton **Paramètres** dans n'importe quel onglet ou utilisez le bouton `Paramètres` du joystick (par défaut : bouton 7).
2. Dans la fenêtre des paramètres :
   - **Exécutable RetroArch** : Parcourez pour sélectionner le fichier `retroarch.exe`.
   - **Cœur RetroArch** : Parcourez pour sélectionner le fichier `fbneo_libretro.dll`.
   - **Mettre à jour toutes les ROMs** : Générer ou mettre à jour les fichiers de titres de ROM pour tous les onglets.
   - **Paramètres du joystick** : Ouvre une sous-fenêtre pour configurer les contrôles du joystick.
   - **Générer les titres de ROM** : Ouvre une sous-fenêtre pour extraire les titres de ROM pour l'onglet actuel.
3. Enregistrez les modifications ou restaurez les paramètres par défaut si nécessaire.

#### Configuration des Contrôles du Joystick
1. Dans la fenêtre des paramètres, cliquez sur **Paramètres du Joystick**.
2. Ajustez les éléments suivants :
   - **Index de l'axe Y du joystick** : Définissez l'axe pour la navigation verticale (-1 pour désactiver).
   - **Délai de défilement rapide** : Temps entre les actions de défilement (0,02–0,2 seconde).
   - **Étapes initiales de défilement rapide** : Nombre d'éléments à sauter lors du défilement rapide (1–15).
   - **Indices des boutons** : Assignez des boutons pour haut, bas, sélectionner, paramètres, onglet précédent, et onglet suivant.
3. Utilisez le bouton **Tester le Joystick** pour vérifier les entrées du joystick.
4. Enregistrez ou restaurez les paramètres par défaut.

#### Génération des Titres de ROM
1. Dans la fenêtre des paramètres, cliquez sur **Générer les Titres de ROM**.
2. Dans la fenêtre de l'extracteur de titres de ROM :
   - **Répertoire des ROMs** : Sélectionnez le répertoire contenant les fichiers ROM.
   - **Fichier XML d'entrée (optionnel)** : Sélectionnez un fichier XML/DAT pour l'extraction des métadonnées.
   - **Répertoire de sortie** : Le répertoire par défaut est celui de l'application.
   - **Nom du fichier de sortie** : Par défaut, le fichier de titres de ROM correspondant à l'onglet (par exemple, `rom_titles_arcade.txt`).
3. Cliquez sur **Extraire les Titres** pour générer le fichier de titres de ROM.
4. La liste des ROM dans l'onglet correspondant sera mise à jour automatiquement.

#### Mise à Jour de Toutes les ROMs
1. Dans la fenêtre des paramètres, cliquez sur **Mettre à jour toutes les ROMs**.
2. L'application générera ou mettra à jour les fichiers de titres de ROM pour tous les onglets en fonction des répertoires de ROMs et des fichiers XML configurés.
3. Un message de succès liste les onglets mis à jour, et des avertissements sont affichés pour toute erreur.

### Dépannage
- **Erreur : "Exécutable RetroArch invalide"** :
  - Assurez-vous que le chemin vers `retroarch.exe` est correct dans la fenêtre des paramètres.
- **Erreur : "Fichier ROM introuvable"** :
  - Vérifiez que le répertoire des ROMs est correctement défini et contient des fichiers `.zip`, `.7z`, ou `.cue`.
- **Joystick non détecté** :
  - Assurez-vous que le joystick est connecté avant de lancer l'application.
  - Utilisez la fonction **Tester le Joystick** pour déboguer.
- **Erreurs de permission refusée** :
  - Exécutez l'application en tant qu'administrateur pour assurer l'accès en écriture au fichier `config.json` et aux répertoires de sortie.
- **Aucune ROM trouvée** :
  - Vérifiez que le répertoire des ROMs est correctement défini et contient des fichiers ROM valides.

### Support
Pour tout problème ou question, contactez : gegecom83@gmail.com
