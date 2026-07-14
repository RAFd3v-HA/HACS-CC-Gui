# CouchControlHACS-GUI

Eigenständiger Fork der Couch-Control-HACS-Integration mit mehrstufiger GUI-Auswahl.

## Kompatibilität

Domain und Schnittstellen bleiben `couch_control`. Dadurch bleibt die bestehende Couch-Control-tvOS-App kompatibel.

## Testinstallation

1. Bestehende originale Couch-Control-Integration in HACS entfernen.
2. Home Assistant neu starten.
3. Diesen Repository-Inhalt in ein eigenes GitHub-Repository hochladen.
4. Repository in HACS als benutzerdefiniertes Repository vom Typ **Integration** eintragen.
5. Integration installieren und Home Assistant neu starten.
6. Unter **Einstellungen → Geräte & Dienste** `Couch Control Entity Filter GUI` hinzufügen.

Die Auswahl erfolgt nacheinander über Bereiche, Geräte und einzelne Entitäten.

