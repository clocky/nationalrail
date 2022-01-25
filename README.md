# Departure Board

A tiny Python script that uses the [Huxley2](https://huxley2.azurewebsites.net)
API to display upcoming rail departures for a given railway station in the UK.

## Installation

### Install Poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

### Install dependencies

```bash
poetry install
```

### Environment variable

Create a local `.env` file with your National Rail Darwin Lite Webservice access token.

```text
ACCESS_TOKEN=<token>
```

## Usage

The following script will show upcoming departures from **Woking**, which has the CRS Station Code, `"WOK"`.

```bash
poetry run python cli.py --crs=wok
```

## Sample output

Images are 250x122 for deployment on an [Pimoroni Inky pHaT](https://shop.pimoroni.com/products/inky-phat?variant=12549254217811) display.

### Station departures
![docs/platform.png](docs/platform.png)

### Platform departure
![docs/service.png](docs/service.png)

Image optimised for 800x480 7" display:

### Station departures
![docs/station.png](docs/station.png)
