import datetime
from lib2to3.refactor import get_all_fix_names
import logging
from dataclasses import dataclass
from urllib.parse import urljoin

import bleach
import dateutil.parser
import requests
from decouple import config


@dataclass
class Server:
    BASE: str = "https://huxley2.azurewebsites.net"


@dataclass
class Service:
    etd: str = ""
    std: str = ""
    origin: str = ""
    destination: str = ""
    platform: str = ""
    is_cancelled: bool = False
    cancel_reason: str = ""
    delay_reason: str = ""
    via: str = ""


class Huxley:
    def __init__(
        self, crs: str, rows: int, expand: bool = False, endpoint: str = "departures"
    ) -> None:
        self.crs: str = crs
        self.rows: int = rows
        self.expand: bool = expand
        self.endpoint: str = endpoint
        self.services = self.get_services()
        return None

    @property
    def crs(self):
        return self._crs

    @crs.setter
    def crs(self, value: str):
        if len(value) < 3:
            raise ValueError("CRS code must be at least 3 characters long.")
        else:
            self._crs = value

    def get_services(self) -> dict:
        services: dict = {}
        url: str = urljoin(Server.BASE, f"/{self.endpoint}/{self.crs}/{self.rows}")
        params = {"expand": self.expand, "accessToken": config("ACCESS_TOKEN")}
        try:
            response: requests.models.Response = requests.get(url, params)
            logging.debug(response.url)
            services = response.json()
        except ValueError as error:
            logging.warning(f'CRS code "{self.crs}" not found. ')
            raise SystemExit from error
        return services

    @property
    def generated_at(self) -> str:
        return self.services["generatedAt"]

    @property
    def location_name(self) -> str:
        return self.services["locationName"]

    @property
    def train_services(self) -> list:
        train_services: list = []
        if self.services["trainServices"] is not None:
            for train_service in self.services["trainServices"]:
                service = Service()
                service.etd = train_service["etd"]
                service.std = train_service["std"]
                service.origin = train_service["origin"][0]["locationName"]
                service.destination = train_service["destination"][0]["locationName"]
                service.is_cancelled = train_service["isCancelled"]
                service.cancel_reason = train_service["cancelReason"]
                service.delay_reason = train_service["delayReason"]
                service.platform = train_service["platform"]
                service.via = train_service["destination"][0]["via"]
                train_services.append(service)
        return train_services

    @property
    def bus_services(self) -> list:
        bus_services: list = []
        if self.services["busServices"] is not None:
            for bus_service in self.services["busServices"]:
                service = Service()
                service.etd = bus_service["etd"]
                service.std = bus_service["std"]
                service.origin = bus_service["origin"][0]["locationName"]
                service.destination = bus_service["destination"][0]["locationName"]
                service.is_cancelled = bus_service["isCancelled"]
                service.cancel_reason = bus_service["cancelReason"]
                service.delay_reason = bus_service["delayReason"]
                service.platform = bus_service["platform"]
                service.via = bus_service["destination"][0]["via"]
                bus_services.append(service)
        return bus_services

    @property
    def nrcc_messages(self) -> list:
        nrcc_messages: list = []
        if self.services["nrccMessages"] is not None:
            for service in self.services["nrccMessages"]:
                text: str = bleach.clean(service["value"], tags=[], strip=True)
                nrcc_messages.append(text)
        return nrcc_messages
