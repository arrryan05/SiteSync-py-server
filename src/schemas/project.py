# schemas/project.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MetricDetail(BaseModel):
    value: str
    recommendedSteps: List[str]

class PerformanceMetrics(BaseModel):
    FCP: MetricDetail
    LCP: MetricDetail
    CLS: MetricDetail
    TBT: MetricDetail

class CodeChange(BaseModel):
    file: str
    startLine: int
    endLine: int
    oldCode: str
    newCode: str
    explanation: str

class AnalysisInsight(BaseModel):
    route: str
    performanceData: List[PerformanceMetrics]
    codeChanges: dict[str, List[CodeChange]] = {}

class CreateProjectRequest(BaseModel):
    website: str
    name: str
    gitUrl: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    website: str
    name: Optional[str] = None
    gitUrl: Optional[str] = None
    analysisSummary: List[AnalysisInsight]
    status: str
    createdAt: datetime
    updatedAt: datetime
