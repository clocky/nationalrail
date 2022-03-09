"""Retrieve and parse data from the National Rail API."""
import datetime
import logging
from dataclasses import dataclass, field
from urllib.parse import urljoin

import bleach
import dateutil.parser
import requests
from decouple import config, UndefinedValueError  # type: ignore


@dataclass
class Server:
    """A server to connect to."""

    BASE: str = "https://huxley2.azurewebsites.net"


@dataclass
class Service:
    """A service."""

    etd: str = ""
    std: str = ""
    origin: str = ""
    destination: str = ""
    destination_crs: str = ""
    platform: str = ""
    is_cancelled: bool = False
    cancel_reason: str = ""
    delay_reason: str = ""
    via: str = ""
    operator: str = ""
    guid: str = ""
    calling_points: dict = field(default_factory=dict)

    @property
    def cancel_reason_short(self) -> str:
        """Return a truncated string of the cancel reason."""
        reason = self.cancel_reason.partition("because of")
        return f"Cancelled due to {reason[2].lstrip()}"

    @property
    def delay_reason_short(self) -> str:
        """Return a truncated string of the delay reason."""
        reason = self.delay_reason.partition("delayed by a")
        return f"Delayed due to {reason[2].lstrip()}"


class Huxley:
    """A class to retrieve and parse data from the Huxley API."""

    def __init__(
        self, crs: str, rows: int, expand: bool = False, endpoint: str = "departures"
    ) -> None:
        """Initialise the Huxley class."""
        self.crs: str = crs
        self.rows: int = rows
        self.expand: bool = expand
        self.endpoint: str = endpoint
        self.services = self.get_services()
        return None

    @property
    def crs(self):
        """Return the CRS code."""
        return self._crs

    @crs.setter
    def crs(self, value: str):
        if len(value) < 3:
            raise ValueError("CRS code must be at least 3 characters long.")
        else:
            self._crs = value

    def get_services(self) -> dict:
        """Return a dictionary of services."""
        services: dict = {}
        url: str = urljoin(Server.BASE, f"/{self.endpoint}/{self.crs}/{self.rows}")
        params = {"expand": str(self.expand)}

        # Append access token to the query if found in environment variables.
        try:
            access_token: str = config("ACCESS_TOKEN")
            params.update({"accessToken": access_token})
        except UndefinedValueError as error:
            logging.warning(error)
            raise SystemExit from error

        # Attempt to to retrieve the data from the API.
        try:
            response: requests.models.Response = requests.get(url, params)
            services = response.json()
        except ValueError as error:
            logging.warning(f'CRS code "{self.crs}" not found. ')
            raise SystemExit from error

        return services

    @property
    def generated_at(self) -> str:
        """Return the date and time the data was generated."""
        return self.services["generatedAt"]

    @property
    def location_name(self) -> str:
        """Return the location name."""
        return self.services["locationName"]

    @property
    def train_services(self) -> list:
        """Return a list of train services."""
        train_services: list = []
        if self.services["trainServices"] is not None:
            for train_service in self.services["trainServices"]:
                service = Service()
                service.etd = train_service["etd"]
                service.std = train_service["std"]
                service.origin = train_service["origin"][0]["locationName"]
                service.destination = train_service["destination"][0]["locationName"]
                service.destination_crs = train_service["destination"][0]["crs"]

                try:
                    if train_service["subsequentCallingPoints"] is not None:
                        service.calling_points = train_service[
                            "subsequentCallingPoints"
                        ]
                except KeyError:
                    service.calling_points = {}

                service.is_cancelled = train_service["isCancelled"]
                service.cancel_reason = train_service["cancelReason"]
                service.delay_reason = train_service["delayReason"]
                service.platform = train_service["platform"]
                service.operator = train_service["operator"]
                service.via = train_service["destination"][0]["via"]
                service.guid = train_service["serviceIdGuid"]
                train_services.append(service)
        return train_services

    @property
    def bus_services(self) -> list:
        """Return a list of bus services."""
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
        """Return a list of NRCC messages."""
        nrcc_messages: list = []
        if self.services["nrccMessages"] is not None:
            for service in self.services["nrccMessages"]:
                text: str = bleach.clean(service["value"], tags=[], strip=True)
                nrcc_messages.append(text)
        return nrcc_messages
