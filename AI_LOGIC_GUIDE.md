# AI Reasoning System - Logic Location & Performance Guide

## 📍 **Where to Find What - Complete Code Location Map**

This document explains exactly where each piece of AI logic is located and how to adjust it for performance.

---

## 🧠 **Question Processing Flow & Code Locations**

### **Step 1: Initial Question Receipt**
**Location**: `modules/web/ai_handlers.py:41-65`
```python
async def intelligent_analysis_handler(self, request: Request) -> Response:
    # Parse request data
    data = await request.json()
    user_question = data.get("question", "")
    analysis_depth = data.get("depth", "standard")
```

**Performance Adjustments**:
- **Line 52**: Add request validation caching
- **Line 55**: Implement request deduplication
- **Line 58**: Add rate limiting logic

---

### **Step 2: Intent Classification**
**Location**: `modules/ai/context_builder.py:65-95`
```python
async def _classify_intent(self, user_query: str) -> str:
    """Classify user intent from query"""
    query_lower = user_query.lower()
    
    # Sales and revenue analysis
    if any(word in query_lower for word in ['sales', 'revenue', 'profit']):
        return "sales_analysis"
    # ... more classifications
```

**Performance Adjustments**:
- **Lines 66-95**: Replace with ML model for faster classification
- **Line 67**: Cache `query_lower` for repeated use
- **Line 70**: Use regex patterns instead of word lists for speed
- **Add at line 65**: Intent caching mechanism

**Performance Optimization Code**:
```python
# Add this before line 65
_intent_cache = {}

async def _classify_intent(self, user_query: str) -> str:
    # Cache check for performance
    cache_key = hashlib.md5(user_query.encode()).hexdigest()
    if cache_key in self._intent_cache:
        return self._intent_cache[cache_key]
    
    # Your existing logic here...
    result = # ... existing classification logic
    
    # Cache the result
    self._intent_cache[cache_key] = result
    return result
```

---

### **Step 3: Context Building**
**Location**: `modules/ai/context_builder.py:53-63`
```python
async def build_context(self, user_query: str) -> PowerBIContext:
    """Build comprehensive context for AI analysis"""
    logger.info(f"Building context for query: {user_query[:50]}...")
    
    # Initialize context
    context = PowerBIContext(
        query=user_query,
        intent=await self._classify_intent(user_query)
    )
    
    # Build context components in parallel where possible
    await self._build_powerbi_context(context)
```

**Performance Adjustments**:
- **Line 56**: Add context caching based on query similarity
- **Line 63**: Parallelize context building tasks
- **Line 64**: Add timeout controls

**Performance Optimization Code**:
```python
# Replace line 63 with parallel execution
import asyncio

# Build context components in parallel
await asyncio.gather(
    self._build_powerbi_context(context),
    self._build_business_context(context),
    self._build_time_context_async(context),  # Make this async
    return_exceptions=True  # Don't fail if one component fails
)
```

---

### **Step 4: Workspace & Dataset Discovery**
**Location**: `modules/ai/context_builder.py:99-132`
```python
async def _find_relevant_datasets(self, context: PowerBIContext):
    """Find datasets relevant to the user query"""
    relevant_datasets = []
    
    # Keywords for different types of analysis
    intent_keywords = {
        "sales_analysis": ["sales", "revenue", "order", "transaction"],
        # ... more keywords
    }
    
    # Search through workspaces for relevant datasets
    for workspace in context.available_workspaces:
        try:
            datasets = await self.powerbi_client.get_datasets(workspace.id)
            # ... dataset scoring logic
```

**Performance Adjustments**:
- **Line 109**: Cache workspace datasets to avoid repeated API calls
- **Line 117**: Limit concurrent workspace searches
- **Line 125**: Add relevance score caching
- **Line 132**: Implement dataset metadata caching

**Performance Optimization Code**:
```python
# Add caching at line 117
_dataset_cache = {}
_cache_ttl = 300  # 5 minutes

async def _find_relevant_datasets(self, context: PowerBIContext):
    cache_key = f"datasets_{hash(tuple(ws.id for ws in context.available_workspaces))}"
    
    if cache_key in self._dataset_cache:
        cache_entry = self._dataset_cache[cache_key]
        if (datetime.now() - cache_entry['timestamp']).seconds < self._cache_ttl:
            context.relevant_datasets = cache_entry['datasets']
            return
    
    # Your existing logic...
    # Cache the results
    self._dataset_cache[cache_key] = {
        'datasets': relevant_datasets,
        'timestamp': datetime.now()
    }
```

---

### **Step 5: AI Reasoning Process**
**Location**: `modules/ai/reasoning_engine.py:64-85`
```python
async def analyze_request(self, user_query: str, analysis_depth: str = "standard") -> AnalysisResult:
    """Main analysis method with complete thinking process"""
    start_time = datetime.now()
    
    try:
        # STEP 1: Build comprehensive context
        logger.debug("Building analysis context...")
        context = await self.context_builder.build_context(user_query)
        
        # STEP 2: Internal reasoning (Hidden from user)
        logger.debug("Performing internal reasoning...")
        thinking_process = await self._internal_reasoning(user_query, context)
```

**Performance Adjustments**:
- **Line 67**: Add analysis result caching
- **Line 72**: Implement context reuse for similar queries
- **Line 76**: Add thinking process caching
- **Line 80**: Optimize execution plan caching

**Performance Optimization Code**:
```python
# Add at beginning of analyze_request method
query_hash = hashlib.md5(f"{user_query}:{analysis_depth}".encode()).hexdigest()

# Check cache first
if query_hash in self._analysis_cache:
    cached_result = self._analysis_cache[query_hash]
    if (datetime.now() - cached_result['timestamp']).seconds < 300:  # 5 min cache
        logger.info("Returning cached analysis result")
        return cached_result['result']

# ... existing logic ...

# Cache the result before returning
self._analysis_cache[query_hash] = {
    'result': result,
    'timestamp': datetime.now()
}
```

---

### **Step 6: Azure OpenAI Communication**
**Location**: `modules/ai/azure_openai_client.py:40-85`
```python
async def reasoning_analysis(self, user_query: str, context: Dict[str, Any]) -> ThinkingProcess:
    """Perform multi-step reasoning analysis with thinking process"""
    reasoning_prompt = self._build_reasoning_prompt(user_query, context)
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": reasoning_prompt}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "response_format": {"type": "json_object"}
            }
```

**Performance Adjustments**:
- **Line 44**: Reuse HTTP sessions instead of creating new ones
- **Line 54**: Reduce max_tokens for faster responses
- **Line 55**: Lower temperature for faster, more deterministic responses
- **Line 46**: Add prompt caching

**Performance Optimization Code**:
```python
# Replace session creation with reused session
class AzureOpenAIClient:
    def __init__(self, config: AzureOpenAIConfig):
        self.config = config
        self._session = None  # Reuse session
        
    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def reasoning_analysis(self, user_query: str, context: Dict[str, Any]) -> ThinkingProcess:
        session = await self._get_session()
        
        # Optimize payload for performance
        payload = {
            "messages": [...],
            "max_tokens": min(self.config.max_tokens, 2000),  # Limit for speed
            "temperature": 0.1,  # Lower for faster responses
            "stream": False  # Disable streaming for speed
        }
```

---

### **Step 7: DAX Query Generation**
**Location**: `modules/ai/azure_openai_client.py:103-138`
```python
async def generate_dax_query(self, intent: str, schema_context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate optimized DAX queries based on user intent and schema"""
    dax_prompt = self._build_dax_generation_prompt(intent, schema_context)
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "messages": [
                    {"role": "system", "content": self._get_dax_system_prompt()},
                    {"role": "user", "content": dax_prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.1,
```

**Performance Adjustments**:
- **Line 106**: Cache DAX queries by intent pattern
- **Line 113**: Reduce max_tokens to 1000 for DAX generation
- **Line 114**: Use temperature 0.0 for consistent DAX output
- **Line 105**: Pre-generate common DAX patterns

**Performance Optimization Code**:
```python
# Add DAX pattern cache
_dax_pattern_cache = {
    "sales_analysis": {
        "top_products": "EVALUATE TOPN(10, SUMMARIZE(Sales, [Product], \"Revenue\", SUM([Amount])), [Revenue], DESC)",
        "sales_trends": "EVALUATE SUMMARIZE(Sales, [Date], \"Total\", SUM([Amount]))",
    },
    "customer_analysis": {
        "top_customers": "EVALUATE TOPN(10, SUMMARIZE(Sales, [Customer], \"Revenue\", SUM([Amount])), [Revenue], DESC)"
    }
}

async def generate_dax_query(self, intent: str, schema_context: Dict[str, Any]) -> Dict[str, Any]:
    # Check if we have a cached pattern
    if intent in self._dax_pattern_cache:
        patterns = self._dax_pattern_cache[intent]
        # Return cached pattern if available
        return {
            "primary_query": patterns.get("default", list(patterns.values())[0]),
            "alternative_queries": list(patterns.values()),
            "explanation": "Using optimized cached pattern",
            "confidence": 0.95
        }
    
    # Fall back to AI generation for complex queries
    # ... existing AI logic
```

---

### **Step 8: Power BI Query Execution**
**Location**: `modules/powerbi/client.py:193-298`
```python
async def execute_dax_query(self, dataset_id: str, dax_query: str, context: Optional[PowerBIContext] = None) -> QueryResult:
    """Execute DAX query against a dataset"""
    start_time = datetime.now()
    
    # Generate query hash for caching/logging
    query_hash = hashlib.md5(f"{dataset_id}:{dax_query}".encode()).hexdigest()
    
    access_token = await self.auth_manager.get_access_token()
```

**Performance Adjustments**:
- **Line 201**: Add result caching for identical queries
- **Line 226**: Reduce timeout for faster failure detection
- **Line 233**: Use connection pooling
- **Line 238**: Add query result compression

**Performance Optimization Code**:
```python
# Add query result caching
_query_cache = {}
_cache_ttl = 600  # 10 minutes for data queries

async def execute_dax_query(self, dataset_id: str, dax_query: str, context: Optional[PowerBIContext] = None) -> QueryResult:
    # Check cache first
    cache_key = hashlib.md5(f"{dataset_id}:{dax_query}".encode()).hexdigest()
    
    if cache_key in self._query_cache:
        cached_entry = self._query_cache[cache_key]
        if (datetime.now() - cached_entry['timestamp']).seconds < self._cache_ttl:
            logger.info(f"Returning cached query result for {cache_key[:8]}...")
            return cached_entry['result']
    
    # Execute query with optimized timeout
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30)  # Faster timeout
    ) as session:
        # ... existing query logic
        
    # Cache successful results
    if result.success:
        self._query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
```

---

### **Step 9: Response Formatting**
**Location**: `modules/ai/response_formatter.py:56-120`
```python
def format_analysis_result(self, analysis_result: AnalysisResult) -> str:
    """Main method to format complete analysis result"""
    logger.debug("Formatting analysis result for Teams...")
    
    if not analysis_result.success:
        return self._format_error_response(analysis_result)
    
    try:
        # Build formatted response sections
        sections = []
        
        # Header section
        if self.options.use_emojis:
            sections.append(self._create_header_section(analysis_result))
```

**Performance Adjustments**:
- **Line 61**: Cache formatted responses for similar results
- **Line 68**: Pre-generate common response templates
- **Line 73**: Optimize emoji and formatting operations
- **Line 80**: Reduce section complexity for speed

**Performance Optimization Code**:
```python
# Add response template cache
_response_templates = {
    "sales_analysis": """📊 **{title}**

**Revenue Leaders:**
{revenue_data}

**💡 Key Insights:**
{insights}

**📈 Recommendations:**
{recommendations}

*Analysis completed in {execution_time}ms*""",
    
    "customer_analysis": """👥 **{title}**

**Top Customers:**
{customer_data}

**💡 Customer Insights:**
{insights}

**📈 Customer Recommendations:**
{recommendations}

*Analysis completed in {execution_time}ms*"""
}

def format_analysis_result(self, analysis_result: AnalysisResult) -> str:
    # Use template for faster formatting
    intent = analysis_result.thinking.user_intent
    base_intent = intent.split('_')[0] + '_analysis'  # sales_analysis, customer_analysis, etc.
    
    if base_intent in self._response_templates:
        template = self._response_templates[base_intent]
        return template.format(
            title=self._format_intent_title(intent),
            revenue_data=self._format_data_quick(analysis_result.data),
            insights='\n'.join(f"• {insight}" for insight in self._extract_insights_quick(analysis_result)),
            recommendations='\n'.join(f"• {rec}" for rec in self._extract_recommendations_quick(analysis_result)),
            execution_time=analysis_result.execution_time_ms
        )
    
    # Fall back to full formatting for complex cases
    return self._full_format_analysis_result(analysis_result)
```

---

## ⚡ **Performance Configuration Settings**

### **Location**: `modules/config/config_manager.py:58-69`
```python
@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration settings"""
    endpoint: str
    api_key: str
    deployment_name: str
    api_version: str = "2024-02-15-preview"
    max_tokens: int = 4000
    temperature: float = 0.3
    thinking_enabled: bool = True
    analysis_depth: str = "standard"
    response_style: str = "business"
```

### **Performance Optimizations by Analysis Depth**

**Fast Performance (< 5 seconds)**:
```python
# In config.json or environment variables
{
    "azure_openai": {
        "max_tokens": 1500,
        "temperature": 0.0,
        "analysis_depth": "standard"
    }
}
```

**Balanced Performance (< 15 seconds)**:
```python
{
    "azure_openai": {
        "max_tokens": 3000,
        "temperature": 0.2,
        "analysis_depth": "deep"
    }
}
```

**Comprehensive Analysis (< 45 seconds)**:
```python
{
    "azure_openai": {
        "max_tokens": 4000,
        "temperature": 0.3,
        "analysis_depth": "extensive"
    }
}
```

---

## 🔧 **Quick Performance Tuning Guide**

### **For Fastest Response Times**:

1. **Enable Caching**: Add these lines to `modules/ai/reasoning_engine.py:30`:
```python
self._analysis_cache = {}
self._context_cache = {}
self._dax_cache = {}
```

2. **Reduce AI Complexity**: In `modules/ai/azure_openai_client.py:54-55`:
```python
"max_tokens": 1500,  # Reduced from 4000
"temperature": 0.0,   # Reduced from 0.3
```

3. **Limit Dataset Search**: In `modules/ai/context_builder.py:133`:
```python
context.relevant_datasets = sorted(relevant_datasets, key=lambda ds: getattr(ds, 'relevance_score', 0), reverse=True)[:2]  # Reduced from 5
```

4. **Use Response Templates**: Replace complex formatting with templates (shown above)

### **For Balanced Performance**:

1. **Implement Connection Pooling**: In `modules/ai/azure_openai_client.py:25`:
```python
self._session_pool = aiohttp.ClientSession()
```

2. **Add Parallel Processing**: In `modules/ai/context_builder.py:63`:
```python
await asyncio.gather(
    self._build_powerbi_context(context),
    self._build_business_context(context),
    self._build_time_context(context)
)
```

3. **Cache DAX Patterns**: Implement the DAX pattern cache shown above

### **Performance Monitoring Locations**:

- **Timing Metrics**: `modules/ai/reasoning_engine.py:65-95`
- **Cache Hit Rates**: Add logging in cache check sections
- **AI Response Times**: `modules/ai/azure_openai_client.py:40-85`
- **Power BI Query Times**: `modules/powerbi/client.py:198-236`

---

## 📊 **Performance Tuning Checklist**

### ✅ **Immediate Wins (< 1 hour)**:
- [ ] Reduce max_tokens to 1500
- [ ] Set temperature to 0.0
- [ ] Limit relevant_datasets to 2
- [ ] Enable HTTP session reuse

### ✅ **Medium Effort (2-4 hours)**:
- [ ] Implement analysis result caching
- [ ] Add DAX pattern caching
- [ ] Create response templates
- [ ] Add parallel context building

### ✅ **Advanced Optimizations (1+ days)**:
- [ ] Implement ML-based intent classification
- [ ] Add database caching layer
- [ ] Optimize Power BI query patterns
- [ ] Implement streaming responses

---

**Key Files for Performance Tuning**:
1. `modules/ai/reasoning_engine.py` - Main orchestration and caching
2. `modules/ai/azure_openai_client.py` - AI communication optimization
3. `modules/ai/context_builder.py` - Context building and dataset search
4. `modules/config/config_manager.py` - Performance configuration settings
5. `modules/powerbi/client.py` - Power BI query optimization

**Most Impact for Least Effort**: Focus on caching in `reasoning_engine.py` and reducing AI complexity in `azure_openai_client.py`.