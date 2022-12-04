# Software des Energiemonitoring-Systems

## Installation mit Docker

Voraussetzungen:
- Linux-Umgebung
- Git
- Docker
- docker-compose


```bash
git clone https://github.com/jm-hsa/plc-connector.git
cd plc-connector
sudo docker-compose build
sudo docker-compose up -d
```

## Installation ohne Docker

Voraussetzungen:
- Git
- Python 3.9
- Python-Paketmanager `pip`
- optional Admin-Rechte (für den `snap7`-Server auf Port 102)
- `influxdb`-Server


```cmd
git clone https://github.com/jm-hsa/plc-connector.git
cd plc-connector
python -m pip install -r requirements.txt
python main.py -c config.yml
```

## Einrichtung des Influxdb-Servers

Der `influxdb`-Server lässt sich unter http://localhost:8086 verwalten. Dort legt man einen Benutzer an und erzeugt anschließend Tokens für die Anwendungen, die auf die Datenbank zugreifen. Über die Explore-Ansicht kann man grafisch individuelle Queries erstellen und dann zu einem Dashboard in z. B. Grafana zusammenstellen.

## Konfiguration

Die PLC-Connector Anwendung wird über die Datei `config.yml` konfiguriert.

Dabei kann eine Auswahl von Modulen aktiviert werden, welche wiederum in drei Kategorien unterteilt sind:

```yaml
Inputs:
  # Eingangsmodule zum Lesen von Messwerten und Anlagenzuständen
  
  # Definiton des ersten Moduls
  #   ClassName: Name der Python-Klasse des Moduls
  #   path.to.module: relativer Importpfad des Input-Moduls
  - ClassName: path.to.module
    # Ob das Modul geladen werden soll
    # Default: True
    enabled: True
    # Parameter, die an den Konstruktor des Moduls übergeben werden
    param1: "value 1"
    param2: "value 2"

  # Definition weiterer Module
  - ClassName2: path.to.module2
    enabled: True

Middlewares:
  # Zwischenmodule zum Verarbeiten von Messwerten und Anlagenzuständen
  
  # Definiton des ersten Moduls
  #   ClassName: Name der Python-Klasse des Moduls
  #   path.to.module: relativer Importpfad des Middleware-Moduls
  - ClassName: path.to.module
    enabled: False

  - TimeCorrelation: time_correlation
    # Zwischenmodule können geschachtelt werden, so dass sie die Ergebnisse des überliegenden Moduls weiterverarbeiten
    submodules:
    - PrintStats: print_stats
      # Standardmäßig werden die Ergebnisse von Middleware-Modulen ohne Untermodulen für die Ausgabe gesammelt und dedupliziert 

Outputs:
  # Ausgabemodule zum Schreiben von Ergebnisse in eine beliebige Anzahl von Datenbanken  
  # Definiton des ersten Moduls
  #   ClassName: Name der Python-Klasse des Moduls
  #   path.to.module: relativer Importpfad des Output-Moduls
  - CSVStorage: csv_file
    path: logs

  - InfluxDB: influxdb
    url: "http://localhost:8086"
    token: "<token>"
    org: "myorg"
    bucket: "energy-monitor"
```

## Input-Module

- `SiemensCPU: siemens.snap7_connect` verbindet sich zu einer Siemens-Steuerung und fragt aktiv einen Datenbaustein ab
  ```yaml
  host: "192.168.0.10" # Addresse der CPU 
  ```
- `SiemensServer: siemens.snap7_server` emuliert eine S7-PLC und stellt passiv Datenbausteine zum Beschreiben bereit
  ```yaml
  port: 102 # Port des S7-Servers 
  ```
- `Balluff: balluff.balluff_html` fragt periodisch einen Balluff IO-Link-Master nach Prozessdaten ab. Sollte wegen schlechter Performance nicht verwendet werden!

- `AllenBradleyCPU: rockwell.allen_bradley_connect` stellt eine EtherNet/IP Verbindung zu einer Compact Logix Steuerung her und fragt aktiv eine Liste von Tags ab
  ```yaml
  host: "192.168.1.10" # Addresse der CPU
  ```

- `Replay: replay_influxdb` gibt aufgezeichnete Messwerte aus einer Influxdb-Datenbank wieder. Dadurch können Messversuche ohne Hardware wiederholt werden
  ```yaml
  # Influxdb Parameter
  url: "http://localhost:8086"
  token: "<token>"
  org: "myorg"
  bucket: "energy-monitor"

  # Zeitstempel, an dem mit der Wiederholung begonnen wird
  start_time: 01.01.2000 00:00:00
  ```

## Middleware-Module

- `PrintStats: print_stats` zeigt Inputstatistiken in der Konsole an. Warnt, wenn ein Input keine Daten liefert.

- `TimeCorrelation: time_correlation` kombiniert mehrere Datenströme zu einem zeitlich monotonen Datensatz. Beispiel:
  ```json
  [
    {"timestamp": "00:00:00", "series": "24V", "value": 123}, 
    {"timestamp": "00:00:02", "series": "24V", "value": 789}
    {"timestamp": "00:00:01", "series": "480V", "value": 456}, 
  ]
  ```
  wird korreliert zu:
  ```json
  [
    {
      "timestamp": "00:00:00",
      "24V": {"value": 123}
    }, 
    {
      "timestamp": "00:00:01", 
      "24V": {"value": 123},
      "480V": {"value": 456}
    }, 
    {
      "timestamp": "00:00:02", 
      "24V": {"value": 789}, 
      "480V": {"value": 456}
    }
  ]
  ```

## Output-Module

Ergebnisse der Middleware-Module werden anhand des `series` Feldes in separaten Messreihen gespeichert. Wenn kein `series` Feld vorhanden ist (z.B. nach `time_correlation`), dann werden alle übrigen Felder als eigenständige Messreihen angesehen. Zu jedem Zeitpunkt kann immer nur ein Messwert (eine CSV-Zeile / ein Influx-Record) je `series` existieren.

- `CSVStorage: csv_file` speichert die Ergebnisse in CSV-Dateien und fügt diese periodisch zu einem ZIP-Ordner hinzu
  ```yaml
  path: logs # Ordner, in dem die Dateien gespeichert werden 
  ```

- `InfluxDB: influxdb` speichert die Ergebnisse in einen Influxdb-bucket.
  ```yaml
  # Influxdb Parameter
  url: "http://localhost:8086"
  token: "<token>"
  org: "myorg"
  bucket: "energy-monitor"
  ```