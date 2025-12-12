"""Hydraulic calculations for pipe geometry and flow."""

import math


def circular_area(diameter_mm: float, depth_mm: float) -> float:
    """Calculate flow area in circular pipe given diameter and depth (mm). Returns area in m²."""
    D = diameter_mm / 1000.0  # convert to meters
    d = depth_mm / 1000.0
    if d <= 0 or D <= 0:
        return 0.0
    if d >= D:
        return math.pi * (D / 2) ** 2
    
    # Partial flow area
    r = D / 2
    theta = 2 * math.acos((r - d) / r)
    area = (r**2 / 2) * (theta - math.sin(theta))
    return area


def compute_flow(area_m2: float, velocity_m_s: float) -> float:
    """Compute flow Q = A * V (m³/s)."""
    return area_m2 * velocity_m_s


def compute_velocity(flow_m3_s: float, area_m2: float) -> float:
    """Compute velocity V = Q / A (m/s)."""
    if area_m2 <= 0:
        return 0.0
    return flow_m3_s / area_m2
