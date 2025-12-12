from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_session
from db.models.core import Project, Site
from app.schemas import ProjectCreate, ProjectResponse, SiteCreate, SiteResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate, session: AsyncSession = Depends(get_session)
) -> Project:
    db_project = Project(**project.model_dump())
    session.add(db_project)
    await session.commit()
    await session.refresh(db_project)
    return db_project


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(session: AsyncSession = Depends(get_session)) -> list[Project]:
    result = await session.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, session: AsyncSession = Depends(get_session)) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/sites", response_model=SiteResponse, status_code=201)
async def create_site(
    project_id: int, site: SiteCreate, session: AsyncSession = Depends(get_session)
) -> Site:
    # Verify project exists
    result = await session.execute(select(Project).where(Project.id == project_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_site = Site(**site.model_dump())
    session.add(db_site)
    await session.commit()
    await session.refresh(db_site)
    return db_site


@router.get("/{project_id}/sites", response_model=list[SiteResponse])
async def list_sites(
    project_id: int, session: AsyncSession = Depends(get_session)
) -> list[Site]:
    result = await session.execute(
        select(Site).where(Site.project_id == project_id).order_by(Site.created_at.desc())
    )
    return list(result.scalars().all())
