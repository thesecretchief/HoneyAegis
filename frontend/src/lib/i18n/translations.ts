export type Locale = "en" | "es" | "de" | "fr" | "el";

export interface Translations {
  // Navigation
  nav_dashboard: string;
  nav_sessions: string;
  nav_alerts: string;
  nav_honey_tokens: string;
  nav_webhooks: string;
  nav_sensors: string;
  nav_marketplace: string;
  nav_config: string;

  // Dashboard
  dashboard_title: string;
  attacks_today: string;
  unique_ips: string;
  auth_successes: string;
  active_sensors: string;
  live_feed: string;
  top_countries: string;
  top_ports: string;
  top_usernames: string;
  attack_map: string;

  // Sessions
  sessions_title: string;
  source_ip: string;
  country: string;
  protocol: string;
  duration: string;
  commands: string;
  risk_score: string;
  no_sessions: string;

  // Alerts
  alerts_title: string;
  severity: string;
  message: string;
  triggered_at: string;
  no_alerts: string;

  // Honey Tokens
  honey_tokens_title: string;
  create_token: string;
  token_type: string;
  token_value: string;
  trigger_count: string;
  active: string;
  inactive: string;

  // Sensors
  sensors_title: string;
  register_sensor: string;
  sensor_id: string;
  sensor_name: string;
  hostname: string;
  ip_address: string;
  status_online: string;
  status_offline: string;
  status_stale: string;

  // Marketplace
  marketplace_title: string;
  search_plugins: string;
  install: string;
  installed: string;
  all_plugins: string;

  // Config
  config_title: string;
  save: string;
  cancel: string;

  // Common
  loading: string;
  error: string;
  retry: string;
  back: string;
  delete: string;
  confirm: string;
  search: string;
  filter: string;
  export_btn: string;
  download: string;
  no_data: string;
  page_not_found: string;
  go_home: string;

  // Threat Intel (Iteration 9)
  threat_intel_title: string;
  lookup_indicator: string;
  feeds_configured: string;
  malicious: string;
  clean: string;
  confidence: string;

  // Sandbox (Iteration 9)
  sandbox_title: string;
  analyze_file: string;
  risk_verdict: string;
  static_analysis: string;
  dynamic_analysis: string;

  // Language
  language: string;
}

export const translations: Record<Locale, Translations> = {
  en: {
    nav_dashboard: "Dashboard",
    nav_sessions: "Sessions",
    nav_alerts: "Alerts",
    nav_honey_tokens: "Honey Tokens",
    nav_webhooks: "Webhooks",
    nav_sensors: "Sensors",
    nav_marketplace: "Marketplace",
    nav_config: "Config",

    dashboard_title: "Dashboard",
    attacks_today: "Attacks Today",
    unique_ips: "Unique IPs",
    auth_successes: "Auth Successes",
    active_sensors: "Active Sensors",
    live_feed: "Live Feed",
    top_countries: "Top Countries",
    top_ports: "Top Ports",
    top_usernames: "Top Usernames",
    attack_map: "Attack Map",

    sessions_title: "Sessions",
    source_ip: "Source IP",
    country: "Country",
    protocol: "Protocol",
    duration: "Duration",
    commands: "Commands",
    risk_score: "Risk Score",
    no_sessions: "No sessions recorded yet.",

    alerts_title: "Alerts",
    severity: "Severity",
    message: "Message",
    triggered_at: "Triggered At",
    no_alerts: "No alerts yet.",

    honey_tokens_title: "Honey Tokens",
    create_token: "Create Token",
    token_type: "Type",
    token_value: "Value",
    trigger_count: "Triggers",
    active: "Active",
    inactive: "Inactive",

    sensors_title: "Fleet Management",
    register_sensor: "Register Sensor",
    sensor_id: "Sensor ID",
    sensor_name: "Name",
    hostname: "Hostname",
    ip_address: "IP Address",
    status_online: "Online",
    status_offline: "Offline",
    status_stale: "Stale",

    marketplace_title: "Plugin Marketplace",
    search_plugins: "Search plugins...",
    install: "Install",
    installed: "Installed",
    all_plugins: "All Plugins",

    config_title: "Configuration",
    save: "Save",
    cancel: "Cancel",

    loading: "Loading...",
    error: "Something went wrong.",
    retry: "Retry",
    back: "Back",
    delete: "Delete",
    confirm: "Confirm",
    search: "Search",
    filter: "Filter",
    export_btn: "Export",
    download: "Download",
    no_data: "No data available.",
    page_not_found: "Page not found",
    go_home: "Back to Dashboard",

    threat_intel_title: "Threat Intelligence",
    lookup_indicator: "Look up indicator",
    feeds_configured: "Feeds Configured",
    malicious: "Malicious",
    clean: "Clean",
    confidence: "Confidence",

    sandbox_title: "Malware Sandbox",
    analyze_file: "Analyze File",
    risk_verdict: "Risk Verdict",
    static_analysis: "Static Analysis",
    dynamic_analysis: "Dynamic Analysis",

    language: "Language",
  },
  es: {
    nav_dashboard: "Panel",
    nav_sessions: "Sesiones",
    nav_alerts: "Alertas",
    nav_honey_tokens: "Tokens Trampa",
    nav_webhooks: "Webhooks",
    nav_sensors: "Sensores",
    nav_marketplace: "Marketplace",
    nav_config: "Config.",

    dashboard_title: "Panel de Control",
    attacks_today: "Ataques Hoy",
    unique_ips: "IPs Unicas",
    auth_successes: "Auth Exitosas",
    active_sensors: "Sensores Activos",
    live_feed: "Feed en Vivo",
    top_countries: "Paises Principales",
    top_ports: "Puertos Principales",
    top_usernames: "Usuarios Principales",
    attack_map: "Mapa de Ataques",

    sessions_title: "Sesiones",
    source_ip: "IP de Origen",
    country: "Pais",
    protocol: "Protocolo",
    duration: "Duracion",
    commands: "Comandos",
    risk_score: "Nivel de Riesgo",
    no_sessions: "No hay sesiones registradas.",

    alerts_title: "Alertas",
    severity: "Severidad",
    message: "Mensaje",
    triggered_at: "Activada",
    no_alerts: "Sin alertas.",

    honey_tokens_title: "Tokens Trampa",
    create_token: "Crear Token",
    token_type: "Tipo",
    token_value: "Valor",
    trigger_count: "Activaciones",
    active: "Activo",
    inactive: "Inactivo",

    sensors_title: "Gestion de Flota",
    register_sensor: "Registrar Sensor",
    sensor_id: "ID del Sensor",
    sensor_name: "Nombre",
    hostname: "Hostname",
    ip_address: "Direccion IP",
    status_online: "En Linea",
    status_offline: "Desconectado",
    status_stale: "Inactivo",

    marketplace_title: "Marketplace de Plugins",
    search_plugins: "Buscar plugins...",
    install: "Instalar",
    installed: "Instalado",
    all_plugins: "Todos los Plugins",

    config_title: "Configuracion",
    save: "Guardar",
    cancel: "Cancelar",

    loading: "Cargando...",
    error: "Algo salio mal.",
    retry: "Reintentar",
    back: "Volver",
    delete: "Eliminar",
    confirm: "Confirmar",
    search: "Buscar",
    filter: "Filtrar",
    export_btn: "Exportar",
    download: "Descargar",
    no_data: "Sin datos disponibles.",
    page_not_found: "Pagina no encontrada",
    go_home: "Volver al Panel",

    threat_intel_title: "Inteligencia de Amenazas",
    lookup_indicator: "Buscar indicador",
    feeds_configured: "Feeds Configurados",
    malicious: "Malicioso",
    clean: "Limpio",
    confidence: "Confianza",

    sandbox_title: "Sandbox de Malware",
    analyze_file: "Analizar Archivo",
    risk_verdict: "Veredicto de Riesgo",
    static_analysis: "Analisis Estatico",
    dynamic_analysis: "Analisis Dinamico",

    language: "Idioma",
  },
  de: {
    nav_dashboard: "Dashboard",
    nav_sessions: "Sitzungen",
    nav_alerts: "Alarme",
    nav_honey_tokens: "Honey Tokens",
    nav_webhooks: "Webhooks",
    nav_sensors: "Sensoren",
    nav_marketplace: "Marktplatz",
    nav_config: "Konfig.",

    dashboard_title: "Dashboard",
    attacks_today: "Angriffe Heute",
    unique_ips: "Eindeutige IPs",
    auth_successes: "Auth Erfolge",
    active_sensors: "Aktive Sensoren",
    live_feed: "Live-Feed",
    top_countries: "Top-Laender",
    top_ports: "Top-Ports",
    top_usernames: "Top-Benutzer",
    attack_map: "Angriffskarte",

    sessions_title: "Sitzungen",
    source_ip: "Quell-IP",
    country: "Land",
    protocol: "Protokoll",
    duration: "Dauer",
    commands: "Befehle",
    risk_score: "Risikobewertung",
    no_sessions: "Noch keine Sitzungen aufgezeichnet.",

    alerts_title: "Alarme",
    severity: "Schweregrad",
    message: "Nachricht",
    triggered_at: "Ausgeloest",
    no_alerts: "Keine Alarme.",

    honey_tokens_title: "Honey Tokens",
    create_token: "Token erstellen",
    token_type: "Typ",
    token_value: "Wert",
    trigger_count: "Ausloesungen",
    active: "Aktiv",
    inactive: "Inaktiv",

    sensors_title: "Flottenverwaltung",
    register_sensor: "Sensor registrieren",
    sensor_id: "Sensor-ID",
    sensor_name: "Name",
    hostname: "Hostname",
    ip_address: "IP-Adresse",
    status_online: "Online",
    status_offline: "Offline",
    status_stale: "Veraltet",

    marketplace_title: "Plugin-Marktplatz",
    search_plugins: "Plugins suchen...",
    install: "Installieren",
    installed: "Installiert",
    all_plugins: "Alle Plugins",

    config_title: "Konfiguration",
    save: "Speichern",
    cancel: "Abbrechen",

    loading: "Laden...",
    error: "Etwas ist schiefgelaufen.",
    retry: "Erneut versuchen",
    back: "Zurueck",
    delete: "Loeschen",
    confirm: "Bestaetigen",
    search: "Suche",
    filter: "Filter",
    export_btn: "Exportieren",
    download: "Herunterladen",
    no_data: "Keine Daten verfuegbar.",
    page_not_found: "Seite nicht gefunden",
    go_home: "Zurueck zum Dashboard",

    threat_intel_title: "Bedrohungsintelligenz",
    lookup_indicator: "Indikator nachschlagen",
    feeds_configured: "Konfigurierte Feeds",
    malicious: "Boesartig",
    clean: "Sauber",
    confidence: "Vertrauen",

    sandbox_title: "Malware-Sandbox",
    analyze_file: "Datei analysieren",
    risk_verdict: "Risikourteil",
    static_analysis: "Statische Analyse",
    dynamic_analysis: "Dynamische Analyse",

    language: "Sprache",
  },
  fr: {
    nav_dashboard: "Tableau de bord",
    nav_sessions: "Sessions",
    nav_alerts: "Alertes",
    nav_honey_tokens: "Honey Tokens",
    nav_webhooks: "Webhooks",
    nav_sensors: "Capteurs",
    nav_marketplace: "Marketplace",
    nav_config: "Config.",

    dashboard_title: "Tableau de Bord",
    attacks_today: "Attaques Aujourd'hui",
    unique_ips: "IPs Uniques",
    auth_successes: "Auth Reussies",
    active_sensors: "Capteurs Actifs",
    live_feed: "Flux en Direct",
    top_countries: "Principaux Pays",
    top_ports: "Principaux Ports",
    top_usernames: "Principaux Utilisateurs",
    attack_map: "Carte des Attaques",

    sessions_title: "Sessions",
    source_ip: "IP Source",
    country: "Pays",
    protocol: "Protocole",
    duration: "Duree",
    commands: "Commandes",
    risk_score: "Score de Risque",
    no_sessions: "Aucune session enregistree.",

    alerts_title: "Alertes",
    severity: "Severite",
    message: "Message",
    triggered_at: "Declenchee",
    no_alerts: "Aucune alerte.",

    honey_tokens_title: "Honey Tokens",
    create_token: "Creer un Token",
    token_type: "Type",
    token_value: "Valeur",
    trigger_count: "Declenchements",
    active: "Actif",
    inactive: "Inactif",

    sensors_title: "Gestion de Flotte",
    register_sensor: "Enregistrer Capteur",
    sensor_id: "ID du Capteur",
    sensor_name: "Nom",
    hostname: "Nom d'hote",
    ip_address: "Adresse IP",
    status_online: "En Ligne",
    status_offline: "Hors Ligne",
    status_stale: "Inactif",

    marketplace_title: "Marketplace de Plugins",
    search_plugins: "Rechercher des plugins...",
    install: "Installer",
    installed: "Installe",
    all_plugins: "Tous les Plugins",

    config_title: "Configuration",
    save: "Enregistrer",
    cancel: "Annuler",

    loading: "Chargement...",
    error: "Une erreur est survenue.",
    retry: "Reessayer",
    back: "Retour",
    delete: "Supprimer",
    confirm: "Confirmer",
    search: "Rechercher",
    filter: "Filtrer",
    export_btn: "Exporter",
    download: "Telecharger",
    no_data: "Aucune donnee disponible.",
    page_not_found: "Page non trouvee",
    go_home: "Retour au Tableau de Bord",

    threat_intel_title: "Renseignement sur les Menaces",
    lookup_indicator: "Rechercher un indicateur",
    feeds_configured: "Feeds Configures",
    malicious: "Malveillant",
    clean: "Propre",
    confidence: "Confiance",

    sandbox_title: "Sandbox Malware",
    analyze_file: "Analyser le Fichier",
    risk_verdict: "Verdict de Risque",
    static_analysis: "Analyse Statique",
    dynamic_analysis: "Analyse Dynamique",

    language: "Langue",
  },
  el: {
    nav_dashboard: "Πίνακας",
    nav_sessions: "Συνεδρίες",
    nav_alerts: "Ειδοποιήσεις",
    nav_honey_tokens: "Honey Tokens",
    nav_webhooks: "Webhooks",
    nav_sensors: "Αισθητήρες",
    nav_marketplace: "Αγορά",
    nav_config: "Ρυθμίσεις",

    dashboard_title: "Πίνακας Ελέγχου",
    attacks_today: "Επιθέσεις Σήμερα",
    unique_ips: "Μοναδικές IPs",
    auth_successes: "Επιτυχείς Συνδέσεις",
    active_sensors: "Ενεργοί Αισθητήρες",
    live_feed: "Ζωντανή Ροή",
    top_countries: "Κορυφαίες Χώρες",
    top_ports: "Κορυφαίες Θύρες",
    top_usernames: "Κορυφαία Ονόματα",
    attack_map: "Χάρτης Επιθέσεων",

    sessions_title: "Συνεδρίες",
    source_ip: "IP Πηγής",
    country: "Χώρα",
    protocol: "Πρωτόκολλο",
    duration: "Διάρκεια",
    commands: "Εντολές",
    risk_score: "Βαθμός Κινδύνου",
    no_sessions: "Δεν υπάρχουν καταγεγραμμένες συνεδρίες.",

    alerts_title: "Ειδοποιήσεις",
    severity: "Σοβαρότητα",
    message: "Μήνυμα",
    triggered_at: "Ενεργοποιήθηκε",
    no_alerts: "Χωρίς ειδοποιήσεις.",

    honey_tokens_title: "Honey Tokens",
    create_token: "Δημιουργία Token",
    token_type: "Τύπος",
    token_value: "Τιμή",
    trigger_count: "Ενεργοποιήσεις",
    active: "Ενεργό",
    inactive: "Ανενεργό",

    sensors_title: "Διαχείριση Στόλου",
    register_sensor: "Εγγραφή Αισθητήρα",
    sensor_id: "ID Αισθητήρα",
    sensor_name: "Όνομα",
    hostname: "Hostname",
    ip_address: "Διεύθυνση IP",
    status_online: "Σε σύνδεση",
    status_offline: "Εκτός σύνδεσης",
    status_stale: "Ανενεργός",

    marketplace_title: "Αγορά Plugins",
    search_plugins: "Αναζήτηση plugins...",
    install: "Εγκατάσταση",
    installed: "Εγκατεστημένο",
    all_plugins: "Όλα τα Plugins",

    config_title: "Ρυθμίσεις",
    save: "Αποθήκευση",
    cancel: "Ακύρωση",

    loading: "Φόρτωση...",
    error: "Κάτι πήγε στραβά.",
    retry: "Επανάληψη",
    back: "Πίσω",
    delete: "Διαγραφή",
    confirm: "Επιβεβαίωση",
    search: "Αναζήτηση",
    filter: "Φίλτρο",
    export_btn: "Εξαγωγή",
    download: "Λήψη",
    no_data: "Δεν υπάρχουν δεδομένα.",
    page_not_found: "Η σελίδα δεν βρέθηκε",
    go_home: "Επιστροφή στον Πίνακα",

    threat_intel_title: "Πληροφορίες Απειλών",
    lookup_indicator: "Αναζήτηση δείκτη",
    feeds_configured: "Ρυθμισμένα Feeds",
    malicious: "Κακόβουλο",
    clean: "Καθαρό",
    confidence: "Εμπιστοσύνη",

    sandbox_title: "Sandbox Κακόβουλου Λογισμικού",
    analyze_file: "Ανάλυση Αρχείου",
    risk_verdict: "Ετυμηγορία Κινδύνου",
    static_analysis: "Στατική Ανάλυση",
    dynamic_analysis: "Δυναμική Ανάλυση",

    language: "Γλώσσα",
  },
};
