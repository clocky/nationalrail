# Departure Board

A tiny Python script that uses the [Huxley2](https://huxley2.azurewebsites.net)
API to display upcoming rail departures for a given railway station in the UK.

## Installation

```bash
python3 -m pip install inky --no-dependencies
python3 -m pip install -r requirements.txt
```

## Usage

The following script will show upcoming departures from **Woking**, which has the CRS Station Code, `"WOK"`.

```bash
python3 nationalrail.py --crs=WOK
```

### Sample output

```text
Time    Destination                Plat    Expected
------  -----------------------  ------  ----------
03:42   Manchester Airport            5     On time
03:46   Manchester Airport            9     On time
04:18   Manchester Airport           13     On time
04:48   York                         10     On time
04:50   Manchester Airport                  On time
04:57   Manchester Airport                  On time
04:57   Oxenholme Lake District           Cancelled
05:04   Blackpool North                     On time
05:05   London Euston                       On time
05:08   Manchester Airport                  On time
```
