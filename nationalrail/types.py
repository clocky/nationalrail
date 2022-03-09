from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
from uuid import UUID
from datetime import datetime


@dataclass
class NrccMessage:
    value: str


@dataclass
class Destination:
    location_name: str
    crs: str
    future_change_to: None
    assoc_is_cancelled: bool
    via: Optional[str] = None


class CoachClass(Enum):
    FIRST = "First"
    STANDARD = "Standard"


class Etd(Enum):
    ON_TIME = "On time"


class Value(Enum):
    ACCESSIBLE = "Accessible"
    STANDARD = "Standard"


@dataclass
class Toilet:
    status: int
    value: Value


@dataclass
class Coach:
    coach_class: CoachClass
    loading: int
    loading_specified: bool
    number: str
    toilet: Optional[Toilet] = None


class Operator(Enum):
    EAST_MIDLANDS_RAILWAY = "East Midlands Railway"
    THAMESLINK = "Thameslink"
    SOUTH_WESTERN_RAILWAY = "South Western Railway"
    GREAT_WESTERN_RAILWAY = "Great Western Railway"
    SOUTHERN = "Southern"
    AVANTI_WEST_COAST = "Avanti West Coast"
    LONDON_OVERGROUND = "London Overground"
    WEST_MIDLANDS_TRAINS = "West Midlands Trains"


class OperatorCode(Enum):
    SW = "SW"
    GW = "GW"
    SN = "SN"
    TL = "TL"
    EM = "EM"
    LM = "LM"
    LO = "LO"
    VT = "VT"


@dataclass
class Formation:
    avg_loading: int
    avg_loading_specified: bool
    coaches: List[Coach]


@dataclass
class TrainService:
    origin: List[Destination]
    destination: List[Destination]
    current_origins: None
    current_destinations: None
    service_id_percent_encoded: str
    service_id_guid: UUID
    service_id_url_safe: str
    sta: None
    eta: None
    std: str
    etd: Etd
    operator: Operator
    operator_code: OperatorCode
    is_circular_route: bool
    is_cancelled: bool
    filter_location_cancelled: bool
    service_type: int
    length: int
    detach_front: bool
    is_reverse_formation: bool
    cancel_reason: None
    delay_reason: None
    service_id: str
    adhoc_alerts: None
    platform: Optional[int] = None
    formation: Optional[Formation] = None
    rsid: Optional[str] = None


@dataclass
class Station:
    train_services: List[TrainService]
    bus_services: None
    ferry_services: None
    generated_at: datetime
    location_name: str
    nrcc_messages: List[NrccMessage]
    crs: str
    filter_location_name: None
    filtercrs: None
    filter_type: int
    platform_available: bool
    are_services_available: bool
