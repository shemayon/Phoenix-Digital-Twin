from backend import constants
from backend.app.idsl.repository import IDSLRepository
from backend.app.models.chat import ChatRequest
from backend.app.services.chatbot import GeminiChatService
from backend.app.services.simulator import SimPyDigitalTwinSimulator


def test_chat_service_returns_contextual_reply() -> None:
    repo = IDSLRepository()
    repo.load_from_excel(constants.SAMPLE_DATA_PATH)
    simulator = SimPyDigitalTwinSimulator(repo)

    service = GeminiChatService(repo, simulator)
    request = ChatRequest(message="How do I address the temperature alarm?", assetId="A001")

    response = service.generate_response(request)

    assert "Asset" in response.reply
    assert response.references
    assert response.recommended_actions

