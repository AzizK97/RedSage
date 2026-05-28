# backend/tests/integration/test_permissions.py

@pytest.mark.asyncio
class TestPermissions:
    
    async def test_non_admin_cannot_delete_users(self, app_client, regular_user):
        """User without admin role denied access"""
        response = await app_client.delete(
            "/api/admin/users/123",
            headers={"Authorization": f"Bearer {regular_user.token}"}
        )
        assert response.status_code == 403
    
    async def test_user_cannot_access_other_threads(self, app_client, user1, user2):
        """User1 cannot see User2's conversation thread"""
        response = await app_client.get(
            f"/api/chat/threads/{user2.thread_id}",
            headers={"Authorization": f"Bearer {user1.token}"}
        )
        assert response.status_code == 403