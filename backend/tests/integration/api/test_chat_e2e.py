# backend/tests/integration/api/test_chat_e2e.py

@pytest.mark.asyncio
class TestChatWorkflow:
    
    async def test_user_sends_message_and_gets_response(self, app_client, mock_redmine_api):
        """E2E: User sends chat message → Agent responds"""
        response = await app_client.post("/api/chat/message", json={
            "message": "What's the status of my projects?",
            "thread_id": "default"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"]  # Agent provided response
        assert "project" in data["response"].lower()  # Expected content
    
    async def test_agent_creates_issue(self, app_client, mock_redmine_api):
        """E2E: User asks to create issue → Agent creates in Redmine"""
        response = await app_client.post("/api/chat/message", json={
            "message": "Create an issue: 'Fix login bug' in project ABC",
            "thread_id": "test_thread"
        })
        
        assert response.status_code == 200
        # Verify issue was created in Redmine
        assert mock_redmine_api.post.called
        call_args = mock_redmine_api.post.call_args
        assert "/issues" in call_args[0][0]
    
    async def test_approval_workflow(self, app_client, mock_redmine_api):
        """E2E: Agent suggests action → User approves → Action executes"""
        # Send message that requires approval
        response = await app_client.post("/api/chat/message", json={
            "message": "Delete the old project"
        })
        
        # Should return interrupts
        data = response.json()
        assert data.get("requires_human") is True
        
        # User approves
        approve_response = await app_client.post(
            f"/api/chat/{data['thread_id']}/approve",
            json={"decision_type": "approve"}
        )
        assert approve_response.status_code == 200