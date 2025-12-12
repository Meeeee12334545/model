from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from db.models.core import Site, TimeSeriesRaw
from app.schemas import UploadSummary
from app.services.ingestion import load_timeseries_from_csv, summarize_timeseries
import pandas as pd
from io import BytesIO

router = APIRouter(prefix="/data", tags=["data"])


@router.post("/upload/{site_id}", response_model=UploadSummary)
async def upload_timeseries(
    site_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> UploadSummary:
    # Verify site exists
    result = await session.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Read file
    content = await file.read()
    try:
        df = pd.read_csv(BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Expect columns: timestamp, and parameter columns (depth, velocity, flow, etc.)
    if "timestamp" not in df.columns:
        raise HTTPException(status_code=400, detail="Missing 'timestamp' column")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    
    # Import time series data
    records = []
    param_cols = [c for c in df.columns if c != "timestamp"]
    
    for _, row in df.iterrows():
        for param in param_cols:
            if pd.notna(row[param]):
                records.append(
                    TimeSeriesRaw(
                        site_id=site_id,
                        parameter=param,
                        timestamp=row["timestamp"],
                        value=float(row[param]),
                        unit=None,
                        source=file.filename,
                    )
                )

    session.add_all(records)
    await session.commit()

    # Generate summary
    summary = summarize_timeseries(df, param_cols)
    return UploadSummary(
        site_id=site_id,
        records_imported=len(records),
        time_range=summary["time_range"],
        parameters=summary["columns"],
    )


@router.get("/timeseries/{site_id}")
async def get_timeseries(
    site_id: int,
    parameter: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    query = select(TimeSeriesRaw).where(TimeSeriesRaw.site_id == site_id)
    if parameter:
        query = query.where(TimeSeriesRaw.parameter == parameter)
    query = query.order_by(TimeSeriesRaw.timestamp)

    result = await session.execute(query)
    records = result.scalars().all()
    
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "parameter": r.parameter,
            "value": r.value,
            "unit": r.unit,
            "qc_flag": r.qc_flag,
        }
        for r in records
    ]
