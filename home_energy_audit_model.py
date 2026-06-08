"""
Home Energy Audit Report — Pydantic Data Model
================================================
Defines the structured schema for a comprehensive home energy audit report.
Designed to support automated PDF generation and LLM-generated summaries.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ConditionRating(str, Enum):
    """Standardised condition scale used across multiple components."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class Priority(str, Enum):
    """Implementation priority for a recommendation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FuelType(str, Enum):
    """Primary energy source / fuel type."""
    ELECTRICITY = "electricity"
    NATURAL_GAS = "natural_gas"
    PROPANE = "propane"
    OIL = "oil"
    WOOD = "wood"
    SOLAR = "solar"
    OTHER = "other"


class WindowType(str, Enum):
    SINGLE_PANE = "single_pane"
    DOUBLE_PANE = "double_pane"
    TRIPLE_PANE = "triple_pane"
    STORM = "storm"


# ---------------------------------------------------------------------------
# Sub-models: Property & Occupancy
# ---------------------------------------------------------------------------

class PropertyDetails(BaseModel):
    """Basic identifying and physical characteristics of the audited property."""

    address: str = Field(
        ...,
        description="Full street address of the property (e.g., '123 Maple St, Springfield, IL 62701')."
    )
    year_built: int = Field(
        ...,
        ge=1800,
        description="Year the home was originally constructed."
    )
    conditioned_area_sqft: float = Field(
        ...,
        gt=0,
        description="Total conditioned floor area in square feet."
    )
    stories: int = Field(
        default=1,
        ge=1,
        description="Number of above-grade stories."
    )
    foundation_type: str = Field(
        ...,
        description="Foundation type (e.g., 'slab', 'crawlspace', 'basement')."
    )
    wall_construction: str = Field(
        ...,
        description="Predominant wall construction type (e.g., 'wood frame 2x4', 'masonry block')."
    )
    num_occupants: int = Field(
        default=1,
        ge=1,
        description="Number of permanent occupants; affects baseline energy benchmarking."
    )


# ---------------------------------------------------------------------------
# Sub-models: Energy Consumption
# ---------------------------------------------------------------------------

class UtilityBill(BaseModel):
    """A single monthly (or billing-period) utility record."""

    period_start: date = Field(..., description="First day of the billing period.")
    period_end: date = Field(..., description="Last day of the billing period.")
    fuel_type: FuelType = Field(..., description="Energy source for this bill.")
    consumption_kwh: Optional[float] = Field(
        None,
        ge=0,
        description="Electrical consumption in kilowatt-hours (kWh). Null for non-electric bills."
    )
    consumption_therms: Optional[float] = Field(
        None,
        ge=0,
        description="Gas consumption in therms. Null for non-gas bills."
    )
    cost_usd: float = Field(..., ge=0, description="Total billed amount in US dollars.")


class EnergyConsumption(BaseModel):
    """Aggregated annual energy use and utility billing history."""

    annual_electricity_kwh: float = Field(
        ...,
        ge=0,
        description="Total electricity consumed over the trailing 12 months (kWh)."
    )
    annual_gas_therms: Optional[float] = Field(
        None,
        ge=0,
        description="Total natural gas consumed over the trailing 12 months (therms). Null if no gas service."
    )
    annual_energy_cost_usd: float = Field(
        ...,
        ge=0,
        description="Combined annual utility spend across all fuels (USD)."
    )
    energy_use_intensity_kbtu_sqft: Optional[float] = Field(
        None,
        ge=0,
        description="Energy Use Intensity (EUI) expressed as kBtu per square foot per year; useful for benchmarking."
    )
    utility_bills: List[UtilityBill] = Field(
        default_factory=list,
        description="Individual monthly/period utility bills used to calculate the annual totals above."
    )
    notes: Optional[str] = Field(
        None,
        description="Free-text notes on data quality, gaps, or unusual consumption patterns."
    )


# ---------------------------------------------------------------------------
# Sub-models: Building Envelope — Insulation
# ---------------------------------------------------------------------------

class InsulationZone(BaseModel):
    """Insulation condition and specifications for a single building zone/location."""

    location: str = Field(
        ...,
        description="Building location (e.g., 'attic', 'rim joist', 'exterior walls', 'basement floor')."
    )
    existing_r_value: Optional[float] = Field(
        None,
        description="Current measured or estimated thermal resistance (R-value). None if unknown."
    )
    recommended_r_value: Optional[float] = Field(
        None,
        description="Code- or audit-recommended R-value for this climate zone."
    )
    insulation_type: Optional[str] = Field(
        None,
        description="Material type (e.g., 'fiberglass batt', 'blown cellulose', 'spray foam')."
    )
    condition: ConditionRating = Field(
        ...,
        description="Observed physical condition of existing insulation."
    )
    deficiencies_noted: Optional[str] = Field(
        None,
        description="Description of gaps, voids, compression, moisture damage, or other deficiencies."
    )


class InsulationAssessment(BaseModel):
    """Complete insulation assessment across all building zones."""

    zones: List[InsulationZone] = Field(
        ...,
        min_length=1,
        description="One entry per assessed insulation zone."
    )
    air_sealing_condition: ConditionRating = Field(
        ...,
        description="Overall air-sealing quality; closely tied to insulation effectiveness."
    )
    blower_door_result_cfm50: Optional[float] = Field(
        None,
        ge=0,
        description="Blower-door test result at 50 Pa (CFM50). Lower values indicate tighter envelope."
    )
    ach50: Optional[float] = Field(
        None,
        ge=0,
        description="Air changes per hour at 50 Pa, derived from blower-door test and house volume."
    )
    llm_summary: Optional[str] = Field(
        None,
        description="LLM-generated plain-language summary of insulation findings for inclusion in the report narrative."
    )


# ---------------------------------------------------------------------------
# Sub-models: HVAC
# ---------------------------------------------------------------------------

class HVACUnit(BaseModel):
    """Details for a single heating or cooling appliance."""

    system_type: str = Field(
        ...,
        description="Equipment category (e.g., 'gas furnace', 'central AC', 'heat pump', 'boiler')."
    )
    fuel_type: FuelType = Field(..., description="Fuel/energy source for this unit.")
    brand_model: Optional[str] = Field(
        None,
        description="Manufacturer and model number if identifiable."
    )
    year_installed: Optional[int] = Field(
        None,
        ge=1950,
        description="Approximate installation year; used to estimate remaining useful life."
    )
    rated_efficiency: Optional[str] = Field(
        None,
        description="Nameplate efficiency rating (e.g., '96% AFUE', '16 SEER', '9.5 HSPF')."
    )
    measured_efficiency: Optional[str] = Field(
        None,
        description="Field-measured efficiency if combustion analysis or other testing was performed."
    )
    condition: ConditionRating = Field(..., description="Overall observed condition of the unit.")
    last_serviced: Optional[date] = Field(
        None,
        description="Date of most recent professional service or tune-up."
    )
    deficiencies_noted: Optional[str] = Field(
        None,
        description="Safety concerns, mechanical faults, or maintenance needs identified during the audit."
    )


class HVACAssessment(BaseModel):
    """HVAC system assessment including duct distribution."""

    units: List[HVACUnit] = Field(
        ...,
        min_length=1,
        description="All heating and cooling units present in the home."
    )
    duct_condition: Optional[ConditionRating] = Field(
        None,
        description="Condition of the duct distribution system. Null if no ducted system exists."
    )
    duct_leakage_cfm25: Optional[float] = Field(
        None,
        ge=0,
        description="Duct leakage measured at 25 Pa (CFM25) via duct blaster test, if performed."
    )
    thermostat_type: Optional[str] = Field(
        None,
        description="Thermostat technology present (e.g., 'manual', 'programmable', 'smart/WiFi')."
    )
    llm_summary: Optional[str] = Field(
        None,
        description="LLM-generated plain-language summary of HVAC findings."
    )


# ---------------------------------------------------------------------------
# Sub-models: Windows & Doors
# ---------------------------------------------------------------------------

class WindowGroup(BaseModel):
    """A group of windows sharing the same type and orientation."""

    orientation: str = Field(
        ...,
        description="Cardinal orientation of this window group (e.g., 'north', 'south', 'east', 'west')."
    )
    window_type: WindowType = Field(..., description="Glazing type for this group.")
    count: int = Field(..., ge=1, description="Number of windows in this group.")
    total_area_sqft: Optional[float] = Field(
        None,
        ge=0,
        description="Approximate combined glazing area (sq ft); used for heat-loss calculations."
    )
    condition: ConditionRating = Field(..., description="Frame and seal condition.")
    has_low_e_coating: Optional[bool] = Field(
        None,
        description="True if low-emissivity (Low-E) coating is present. None if unknown."
    )


class WindowDoorAssessment(BaseModel):
    """Assessment of windows and exterior doors."""

    window_groups: List[WindowGroup] = Field(
        default_factory=list,
        description="Windows grouped by type and orientation."
    )
    exterior_door_condition: Optional[ConditionRating] = Field(
        None,
        description="Overall condition of exterior doors including weatherstripping."
    )
    door_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of exterior doors."
    )
    llm_summary: Optional[str] = Field(
        None,
        description="LLM-generated summary of window and door findings."
    )


# ---------------------------------------------------------------------------
# Sub-models: Appliances & Lighting
# ---------------------------------------------------------------------------

class ApplianceItem(BaseModel):
    """An individual major appliance or lighting system."""

    name: str = Field(
        ...,
        description="Appliance or system name (e.g., 'refrigerator', 'clothes dryer', 'LED lighting')."
    )
    year_installed: Optional[int] = Field(None, description="Approximate installation/purchase year.")
    energy_star_certified: Optional[bool] = Field(
        None,
        description="True if ENERGY STAR certified. None if unknown."
    )
    estimated_annual_kwh: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated annual electricity consumption for this appliance (kWh)."
    )
    condition: ConditionRating = Field(..., description="Observed operating condition.")
    notes: Optional[str] = Field(None, description="Auditor notes on this appliance.")


class ApplianceLightingAssessment(BaseModel):
    """Assessment of major appliances and interior lighting."""

    appliances: List[ApplianceItem] = Field(
        default_factory=list,
        description="List of assessed major appliances."
    )
    percent_led_lighting: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Estimated percentage of light fixtures using LED bulbs."
    )
    llm_summary: Optional[str] = Field(
        None,
        description="LLM-generated summary of appliance and lighting findings."
    )


# ---------------------------------------------------------------------------
# Sub-models: Water Heating
# ---------------------------------------------------------------------------

class WaterHeaterAssessment(BaseModel):
    """Domestic hot-water system details."""

    heater_type: str = Field(
        ...,
        description="Water heater type (e.g., 'storage tank', 'tankless', 'heat pump water heater')."
    )
    fuel_type: FuelType = Field(..., description="Energy source for water heating.")
    year_installed: Optional[int] = Field(None, description="Installation year.")
    rated_efficiency_ef_or_uef: Optional[float] = Field(
        None,
        ge=0,
        description="Energy Factor (EF) or Uniform Energy Factor (UEF) from nameplate."
    )
    tank_size_gallons: Optional[float] = Field(
        None,
        ge=0,
        description="Storage capacity in gallons. Null for tankless systems."
    )
    pipe_insulation_present: Optional[bool] = Field(
        None,
        description="True if hot-water pipes are insulated."
    )
    condition: ConditionRating = Field(..., description="Observed condition of the water heater.")
    llm_summary: Optional[str] = Field(
        None,
        description="LLM-generated summary of water heating findings."
    )


# ---------------------------------------------------------------------------
# Sub-models: Renewable Energy
# ---------------------------------------------------------------------------

class RenewableEnergyAssessment(BaseModel):
    """Existing renewable energy systems and solar potential."""

    solar_pv_installed: bool = Field(
        default=False,
        description="True if a photovoltaic (solar) system is already installed."
    )
    solar_pv_capacity_kw: Optional[float] = Field(
        None,
        ge=0,
        description="Installed PV system capacity in kilowatts-peak. Null if not installed."
    )
    solar_pv_annual_production_kwh: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated or metered annual PV production (kWh)."
    )
    solar_suitability_score: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Auditor score 1–10 for solar installation suitability (roof orientation, shading, structural)."
    )
    other_renewables: Optional[str] = Field(
        None,
        description="Description of other on-site renewables (e.g., solar thermal, small wind)."
    )


# ---------------------------------------------------------------------------
# Sub-models: Recommendations
# ---------------------------------------------------------------------------

class Recommendation(BaseModel):
    """A single actionable improvement recommendation."""

    category: str = Field(
        ...,
        description="Category/section this recommendation belongs to (e.g., 'insulation', 'hvac', 'windows', 'appliances', 'water_heating', 'renewables', 'behavior')."
    )
    title: str = Field(
        ...,
        description="Short headline for the recommendation (e.g., 'Add attic insulation to R-49')."
    )
    description: str = Field(
        ...,
        description="Detailed description of the recommended action, including scope and method."
    )
    priority: Priority = Field(
        ...,
        description="Implementation priority based on cost-effectiveness and urgency."
    )
    estimated_cost_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated installed cost in USD before incentives."
    )
    estimated_annual_savings_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Projected annual utility savings in USD after implementation."
    )
    estimated_annual_savings_kwh: Optional[float] = Field(
        None,
        ge=0,
        description="Projected annual energy savings in kWh."
    )
    simple_payback_years: Optional[float] = Field(
        None,
        ge=0,
        description="Simple payback period = estimated_cost / estimated_annual_savings (years)."
    )
    available_incentives: Optional[str] = Field(
        None,
        description="Applicable rebates, tax credits, or financing programs (e.g., 'Federal IRA 25C tax credit up to $1,200')."
    )
    co2_reduction_kg_per_year: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated annual CO₂-equivalent reduction in kilograms."
    )


# ---------------------------------------------------------------------------
# Top-level Report Model
# ---------------------------------------------------------------------------

class HomeEnergyAuditReport(BaseModel):
    """
    Root model for a complete Home Energy Audit Report.
    All section sub-models are included here; optional sections may be omitted
    if not assessed during the audit.
    """

    # ---- Report metadata ----
    report_id: str = Field(
        ...,
        description="Unique identifier for this report (UUID or auditor-assigned reference number)."
    )
    audit_date: date = Field(
        ...,
        description="Date on which the on-site audit was performed."
    )
    report_date: date = Field(
        ...,
        description="Date this report was finalised and issued to the client."
    )
    auditor_name: str = Field(
        ...,
        description="Full name of the certified energy auditor who performed the assessment."
    )
    auditor_certification: Optional[str] = Field(
        None,
        description="Auditor credential/certification (e.g., 'BPI Building Analyst', 'RESNET HERS Rater')."
    )
    auditing_company: Optional[str] = Field(
        None,
        description="Name of the company or organisation that conducted the audit."
    )

    # ---- Property & consumption ----
    property_details: PropertyDetails = Field(
        ...,
        description="Physical and identifying characteristics of the audited property."
    )
    energy_consumption: EnergyConsumption = Field(
        ...,
        description="Annual energy use data and utility billing history."
    )

    # ---- Building envelope & systems ----
    insulation: InsulationAssessment = Field(
        ...,
        description="Insulation levels, air sealing, and blower-door test results."
    )
    hvac: HVACAssessment = Field(
        ...,
        description="Heating, ventilation, and air-conditioning system assessment."
    )
    windows_doors: WindowDoorAssessment = Field(
        ...,
        description="Window and exterior door condition and performance."
    )
    water_heating: WaterHeaterAssessment = Field(
        ...,
        description="Domestic hot-water system details and efficiency."
    )
    appliances_lighting: ApplianceLightingAssessment = Field(
        ...,
        description="Major appliances and lighting system assessment."
    )

    # ---- Renewables (optional) ----
    renewables: Optional[RenewableEnergyAssessment] = Field(
        None,
        description="Existing renewable energy systems and on-site solar potential. Omit if not assessed."
    )

    # ---- Recommendations ----
    recommendations: List[Recommendation] = Field(
        ...,
        min_length=1,
        description="Prioritised list of improvement recommendations across all categories."
    )

    # ---- Summary & scoring ----
    home_energy_score: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="DOE Home Energy Score (1–10) if assessed; 10 is most efficient."
    )
    hers_index: Optional[int] = Field(
        None,
        ge=0,
        description="RESNET HERS Index if rated; lower values indicate greater efficiency (100 = code-built reference home)."
    )
    executive_summary: Optional[str] = Field(
        None,
        description="LLM-generated or auditor-written plain-language executive summary for the homeowner."
    )
    total_estimated_savings_usd_per_year: Optional[float] = Field(
        None,
        ge=0,
        description="Sum of estimated annual savings across all recommendations (USD)."
    )
    total_estimated_investment_usd: Optional[float] = Field(
        None,
        ge=0,
        description="Sum of estimated implementation costs across all recommendations (USD)."
    )
