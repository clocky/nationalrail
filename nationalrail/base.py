import datetime
import logging
from dataclasses import dataclass
from sys import settrace
from urllib.parse import urljoin

import bleach
import dateutil.parser
import requests


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
        return None

    @property
    def crs(self):
        return self._crs

    @crs.setter
    def crs(self, value: str):
        if len(value) < 3:
            raise ValueError(f"CRS code must be at least 3 characters long.")
        else:
            self._crs = value

    @property
    def services(self) -> dict:
        """Get train services for a known CRS code."""
        services: dict = {}
        url: str = urljoin(Server.BASE, f"/{self.endpoint}/{self.crs}/{self.rows}")
        params = {"expand": self.expand}
        try:
            response: requests.models.Response = requests.get(url, params)
            services = response.json()
        except ValueError as error:
            logging.warning(f'CRS code "{self.crs}" not found. ')
            raise SystemExit from error
        return services

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
    def nrcc_messages(self) -> list:
        nrcc_messages: list = []
        if self.services["nrccMessages"] is not None:
            for service in self.services["nrccMessages"]:
                text: str = bleach.clean(service["value"], tags=[], strip=True)
                nrcc_messages.append(text)
        return nrcc_messages
