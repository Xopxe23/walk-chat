from httpx import AsyncClient


async def test_swagger(
    async_client: AsyncClient,
):
    response = await async_client.get("/docs")
    assert response.status_code == 200
