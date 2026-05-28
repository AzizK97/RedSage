# backend/tests/unit/agent/test_supervisor.py

@pytest.mark.asyncio
class TestSupervisor:
    
    async def test_overview_agent_selected_for_summary_questions(self):
        """Agent selects Overview agent for 'summarize project' type questions"""
        # This tests the router logic
        pass
    
    async def test_tasks_agent_creates_issues(self):
        """Tasks agent can create issues via tools"""
        pass
    
    async def test_agent_fallback_on_tool_error(self):
        """If tool fails, agent handles gracefully"""
        pass

# backend/tests/unit/tools/test_write_tools.py

@pytest.mark.asyncio
class TestWriteTools:
    
    async def test_create_issue_retry_on_network_error(self, mock_redmine_api_with_error):
        """Tool retries on network error"""
        # Mock first call fails, second succeeds
        pass
    
    async def test_update_issue_validation(self):
        """Tool validates issue_id exists"""
        pass