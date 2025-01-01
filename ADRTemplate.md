# ADR 001: Wahl des Datenbank-Systems

## Status
Entschieden (2024-12-28)

## Kontext
Unser Projekt benötigt eine hochverfügbare und skalierbare Datenbanklösung 
für ein E-Commerce-System mit schnellem Wachstum. Wir müssen große 
Datenmengen in Echtzeit verarbeiten können.

## Entscheidung
Wir wählen PostgreSQL als Hauptdatenbank aus folgenden Gründen:
1. **SQL-Standard und Stabilität**: PostgreSQL ist konform zum SQL-Standard 
   und hat sich seit Jahren in Produktionsumgebungen bewährt.
2. **Erweiterbarkeit**: Es bietet zahlreiche Erweiterungen (z. B. PostGIS) 
   und lässt sich über Plugins flexibel ausbauen.
3. **Community-Unterstützung**: Große und aktive Open-Source-Community, 
   wodurch schnelle Fehlerbehebungen und neue Features möglich sind.

## Alternativen
1. **MySQL**: Ebenfalls weit verbreitet, allerdings schwächere Unterstützung 
   für erweiterte SQL-Features und weniger flexibel bei Erweiterungen.
2. **MongoDB**: Non-Relational-Store, gute Skalierbarkeit, jedoch höherer 
   Entwicklungsaufwand bei komplexen Transaktionen.

## Auswirkungen
- **Positiv**: Stabiler Betrieb, große Community, bekannte Skalierungsszenarien.
- **Negativ**: Evtl. höherer Konfigurationsaufwand (z. B. Tuning von Parametern 
  wie Work-Memory und Autovacuum).

## Konsequenzen
- Wir richten ein zentrales PostgreSQL-Cluster ein, 
  das bei Bedarf horizontal skaliert werden kann (z. B. mittels Replikation).
- Die Entwicklungsumgebung wird darauf ausgerichtet, 
  um lokale Tests und Migrations-Skripte leicht zu unterstützen.
