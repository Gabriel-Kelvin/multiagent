from typing import Dict, Any, List
from app.logging_utils import JsonSqlLogger
from mcp_client import call_mcp_tool_sync


def run(state: Dict[str, Any], settings, logger: JsonSqlLogger) -> Dict[str, Any]:
    run_id = state.get("run_id", "")
    nlp_query = state.get("query") or ""
    # Try NLP query first if present; on failure, fall back to SELECT * FROM DATA_TABLE
    tried_queries: List[str] = []
    
    def _exec_via_mcp(q: str) -> List[Dict[str, Any]]:
        """Execute query via MCP db.query_supabase tool"""
        # Build MCP tool arguments with connection parameters
        mcp_args = {
            "query": q,
            "limit": 500,
        }
        
        # Pass connection parameters if available
        if getattr(settings, "DATA_DB_TYPE", ""):
            mcp_args["db_type"] = settings.DATA_DB_TYPE
        if getattr(settings, "DATA_DSN", ""):
            mcp_args["dsn"] = settings.DATA_DSN
        if getattr(settings, "DATA_HOST", ""):
            mcp_args["host"] = settings.DATA_HOST
        if getattr(settings, "DATA_PORT", ""):
            mcp_args["port"] = int(settings.DATA_PORT) if settings.DATA_PORT else None
        if getattr(settings, "DATA_NAME", ""):
            mcp_args["name"] = settings.DATA_NAME
        if getattr(settings, "DATA_USER", ""):
            mcp_args["user"] = settings.DATA_USER
        if getattr(settings, "DATA_PASSWORD", ""):
            mcp_args["password"] = settings.DATA_PASSWORD
        if getattr(settings, "DATA_SSLMODE", ""):
            mcp_args["sslmode"] = settings.DATA_SSLMODE
        
        result = call_mcp_tool_sync("db", "db.query_supabase", mcp_args)
        
        if result.get("status") == "success":
            return result.get("rows", [])
        else:
            raise Exception(result.get("error", "Unknown error from MCP"))
    
    try:
        # MongoDB path: sample documents (basic support - fallback to direct call)
        if str(getattr(settings, "DATA_DB_TYPE", "")).strip().lower() == "mongodb":
            try:
                from utils import mongo_utils
                rows = mongo_utils.sample_rows(settings, limit=500)
                logger.info(run_id, "db", "mongo_sampled", {"rows": len(rows)})
                return {"status": "success", "data": {"rows": rows, "query_used": "mongodb_sample"}, "log": {"rows": len(rows)}}
            except Exception as e:
                logger.exception(run_id, "db", "mongo_error", {"error": str(e)})
                return {"status": "error", "data": {}, "log": {"error": str(e)}}
        
        # Use MCP for SQL queries (PostgreSQL/MySQL/SQLite)
        if nlp_query:
            tried_queries.append(nlp_query)
            try:
                rows = _exec_via_mcp(nlp_query)
                logger.info(run_id, "db", "db_query_executed_mcp", {"rows": len(rows), "via": "mcp"})
                return {"status": "success", "data": {"rows": rows, "query_used": nlp_query}, "log": {"rows": len(rows)}}
            except Exception as e:
                logger.error(run_id, "db", "db_nlp_query_failed", {"error": str(e), "query": nlp_query})
        
        table = getattr(settings, "DATA_TABLE", "")
        if not table:
            return {"status": "error", "data": {}, "log": {"error": "No DATA_TABLE configured and NLP query failed/absent"}}
        
        fallback = f"SELECT * FROM {table}"
        tried_queries.append(fallback)
        rows = _exec_via_mcp(fallback)
        logger.info(run_id, "db", "db_query_executed_fallback_mcp", {"rows": len(rows), "via": "mcp"})
        return {"status": "success", "data": {"rows": rows, "query_used": fallback}, "log": {"rows": len(rows)}}
    except Exception as e:
        logger.exception(run_id, "db", "db_error", {"error": str(e), "tried": tried_queries})
        return {"status": "error", "data": {}, "log": {"error": str(e)}}
