"""
Power BI data models and structures
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class WorkspaceInfo:
    """Power BI workspace information"""
    id: str
    name: str
    description: Optional[str] = None
    is_personal: bool = False
    capacity_id: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None
    is_read_only: bool = False
    is_on_dedicated_capacity: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_personal": self.is_personal,
            "capacity_id": self.capacity_id,
            "type": self.type,
            "state": self.state,
            "is_read_only": self.is_read_only,
            "is_on_dedicated_capacity": self.is_on_dedicated_capacity
        }

@dataclass
class DatasetInfo:
    """Power BI dataset information"""
    id: str
    name: str
    workspace_id: str
    workspace_name: str
    configured_by: Optional[str] = None
    created_date: Optional[str] = None
    content_provider_type: Optional[str] = None
    is_refreshable: bool = True
    is_effective_identity_required: bool = False
    is_effective_identity_roles_required: bool = False
    tables: List[Dict[str, Any]] = field(default_factory=list)
    measures: List[Dict[str, Any]] = field(default_factory=list)
    last_refresh: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "configured_by": self.configured_by,
            "created_date": self.created_date,
            "content_provider_type": self.content_provider_type,
            "is_refreshable": self.is_refreshable,
            "is_effective_identity_required": self.is_effective_identity_required,
            "is_effective_identity_roles_required": self.is_effective_identity_roles_required,
            "tables": self.tables,
            "measures": self.measures,
            "last_refresh": self.last_refresh
        }

@dataclass
class TableInfo:
    """Power BI table information"""
    name: str
    description: Optional[str] = None
    is_hidden: bool = False
    columns: List[Dict[str, Any]] = field(default_factory=list)
    measures: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "is_hidden": self.is_hidden,
            "columns": self.columns,
            "measures": self.measures
        }

@dataclass
class QueryResult:
    """Result from a DAX query execution"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    dataset_id: Optional[str] = None
    dataset_name: Optional[str] = None
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    row_count: int = 0
    query_hash: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "row_count": self.row_count,
            "query_hash": self.query_hash,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class PowerBIContext:
    """Context for Power BI operations"""
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    dataset_id: Optional[str] = None
    dataset_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata
        }