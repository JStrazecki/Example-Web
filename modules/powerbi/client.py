"""
Modular Power BI Client
Handles Power BI API interactions with improved error handling and caching
"""

import logging
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime

import aiohttp

from ..auth import PowerBIAuthManager
from .models import WorkspaceInfo, DatasetInfo, QueryResult, PowerBIContext

logger = logging.getLogger(__name__)

class PowerBIClient:
    """Modular Power BI API client"""
    
    def __init__(self, auth_manager: PowerBIAuthManager):
        self.auth_manager = auth_manager
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        self._workspace_cache = {}
        self._dataset_cache = {}
    
    async def get_workspaces(self, force_refresh: bool = False) -> List[WorkspaceInfo]:
        """Get list of accessible workspaces"""
        if not force_refresh and "workspaces" in self._workspace_cache:
            cached_data = self._workspace_cache["workspaces"]
            # Cache for 10 minutes
            if (datetime.now() - cached_data["timestamp"]).seconds < 600:
                logger.debug("Using cached workspace data")
                return cached_data["data"]
        
        access_token = await self.auth_manager.get_access_token()
        if not access_token:
            logger.error("No access token available for workspace listing")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/groups",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        workspaces = []
                        
                        for ws in data.get("value", []):
                            workspace = WorkspaceInfo(
                                id=ws["id"],
                                name=ws["name"],
                                description=ws.get("description"),
                                is_personal=ws.get("isPersonal", False),
                                capacity_id=ws.get("capacityId"),
                                type=ws.get("type", "Workspace"),
                                state=ws.get("state", "Active"),
                                is_read_only=ws.get("isReadOnly", False),
                                is_on_dedicated_capacity=ws.get("isOnDedicatedCapacity", False)
                            )
                            
                            if workspace.state == "Active":
                                workspaces.append(workspace)
                        
                        # Cache the results
                        self._workspace_cache["workspaces"] = {
                            "data": workspaces,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info(f"Retrieved {len(workspaces)} active workspaces")
                        return workspaces
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get workspaces: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching workspaces: {e}", exc_info=True)
            return []
    
    async def get_workspace_by_name(self, workspace_name: str) -> Optional[WorkspaceInfo]:
        """Find workspace by name"""
        workspaces = await self.get_workspaces()
        
        for workspace in workspaces:
            if workspace.name.lower() == workspace_name.lower():
                return workspace
        
        logger.warning(f"Workspace '{workspace_name}' not found")
        return None
    
    async def get_datasets(self, workspace_id: str, force_refresh: bool = False) -> List[DatasetInfo]:
        """Get datasets in a workspace"""
        cache_key = f"datasets_{workspace_id}"
        
        if not force_refresh and cache_key in self._dataset_cache:
            cached_data = self._dataset_cache[cache_key]
            # Cache for 5 minutes
            if (datetime.now() - cached_data["timestamp"]).seconds < 300:
                logger.debug(f"Using cached dataset data for workspace {workspace_id}")
                return cached_data["data"]
        
        access_token = await self.auth_manager.get_access_token()
        if not access_token:
            logger.error("No access token available for dataset listing")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Handle personal workspace differently
            if workspace_id == "me":
                url = f"{self.base_url}/datasets"
                workspace_name = "My Workspace"
            else:
                url = f"{self.base_url}/groups/{workspace_id}/datasets"
                # Get workspace name for context
                workspaces = await self.get_workspaces()
                workspace_name = next(
                    (ws.name for ws in workspaces if ws.id == workspace_id),
                    "Unknown Workspace"
                )
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        datasets = []
                        
                        for ds in data.get("value", []):
                            dataset = DatasetInfo(
                                id=ds["id"],
                                name=ds["name"],
                                workspace_id=workspace_id,
                                workspace_name=workspace_name,
                                configured_by=ds.get("configuredBy"),
                                created_date=ds.get("createdDate"),
                                content_provider_type=ds.get("contentProviderType"),
                                is_refreshable=ds.get("isRefreshable", True),
                                is_effective_identity_required=ds.get("isEffectiveIdentityRequired", False),
                                is_effective_identity_roles_required=ds.get("isEffectiveIdentityRolesRequired", False)
                            )
                            datasets.append(dataset)
                        
                        # Cache the results
                        self._dataset_cache[cache_key] = {
                            "data": datasets,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info(f"Retrieved {len(datasets)} datasets from workspace {workspace_name}")
                        return datasets
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get datasets: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching datasets for workspace {workspace_id}: {e}", exc_info=True)
            return []
    
    async def get_dataset_by_name(self, workspace_id: str, dataset_name: str) -> Optional[DatasetInfo]:
        """Find dataset by name in a workspace"""
        datasets = await self.get_datasets(workspace_id)
        
        for dataset in datasets:
            if dataset.name.lower() == dataset_name.lower():
                return dataset
        
        logger.warning(f"Dataset '{dataset_name}' not found in workspace {workspace_id}")
        return None
    
    async def execute_dax_query(self, 
                               dataset_id: str, 
                               dax_query: str,
                               context: Optional[PowerBIContext] = None) -> QueryResult:
        """Execute DAX query against a dataset"""
        start_time = datetime.now()
        
        # Generate query hash for caching/logging
        query_hash = hashlib.md5(f"{dataset_id}:{dax_query}".encode()).hexdigest()
        
        access_token = await self.auth_manager.get_access_token()
        if not access_token:
            return QueryResult(
                success=False,
                error="No access token available",
                query_hash=query_hash
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "queries": [{
                    "query": dax_query
                }],
                "serializerSettings": {
                    "includeNulls": True
                }
            }
            
            logger.info(f"Executing DAX query on dataset {dataset_id[:8]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/datasets/{dataset_id}/executeQueries",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if "results" in data and len(data["results"]) > 0:
                            result = data["results"][0]
                            
                            if "tables" in result and len(result["tables"]) > 0:
                                table = result["tables"][0]
                                rows = table.get("rows", [])
                                
                                logger.info(f"DAX query successful: {len(rows)} rows in {execution_time}ms")
                                
                                return QueryResult(
                                    success=True,
                                    data=rows,
                                    row_count=len(rows),
                                    execution_time_ms=execution_time,
                                    dataset_id=dataset_id,
                                    dataset_name=context.dataset_name if context else None,
                                    workspace_id=context.workspace_id if context else None,
                                    workspace_name=context.workspace_name if context else None,
                                    query_hash=query_hash
                                )
                            else:
                                return QueryResult(
                                    success=True,
                                    data=[],
                                    row_count=0,
                                    execution_time_ms=execution_time,
                                    dataset_id=dataset_id,
                                    query_hash=query_hash
                                )
                        else:
                            return QueryResult(
                                success=False,
                                error="No results returned from query",
                                execution_time_ms=execution_time,
                                query_hash=query_hash
                            )
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"DAX query failed: {response.status} - {error_text}")
                        
                        return QueryResult(
                            success=False,
                            error=f"Query failed with status {response.status}: {error_text[:200]}",
                            execution_time_ms=execution_time,
                            query_hash=query_hash
                        )
                        
        except Exception as e:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"Error executing DAX query: {e}", exc_info=True)
            
            return QueryResult(
                success=False,
                error=f"Error executing query: {str(e)}",
                execution_time_ms=execution_time,
                query_hash=query_hash
            )
    
    async def validate_connection(self) -> Dict[str, Any]:
        """Validate Power BI connection and permissions"""
        validation_result = {
            "auth_configured": self.auth_manager.is_configured(),
            "token_acquired": False,
            "api_accessible": False,
            "workspaces_accessible": False,
            "workspace_count": 0,
            "errors": [],
            "warnings": []
        }
        
        if not validation_result["auth_configured"]:
            validation_result["errors"].append("Authentication not configured")
            return validation_result
        
        # Test token acquisition
        token = await self.auth_manager.get_access_token()
        if token:
            validation_result["token_acquired"] = True
            
            # Test API access
            try:
                workspaces = await self.get_workspaces(force_refresh=True)
                validation_result["api_accessible"] = True
                validation_result["workspace_count"] = len(workspaces)
                
                if workspaces:
                    validation_result["workspaces_accessible"] = True
                else:
                    validation_result["warnings"].append("No workspaces accessible - check permissions")
                    
            except Exception as e:
                validation_result["errors"].append(f"API access error: {str(e)}")
        else:
            validation_result["errors"].append("Failed to acquire access token")
        
        return validation_result
    
    def clear_cache(self):
        """Clear all cached data"""
        self._workspace_cache.clear()
        self._dataset_cache.clear()
        logger.info("Power BI client cache cleared")