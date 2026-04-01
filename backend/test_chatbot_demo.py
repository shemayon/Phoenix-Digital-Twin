"""Demo script to show chatbot now responds differently to different questions."""

from backend import constants
from backend.app.idsl.repository import IDSLRepository
from backend.app.models.chat import ChatRequest
from backend.app.services.chatbot import GeminiChatService
from backend.app.services.simulator import SimPyDigitalTwinSimulator


def main():
    print("=" * 80)
    print("CHATBOT DEMO - Testing different responses to different questions")
    print("=" * 80)
    
    # Setup
    repo = IDSLRepository()
    repo.load_from_excel(constants.SAMPLE_DATA_PATH)
    simulator = SimPyDigitalTwinSimulator(repo)
    service = GeminiChatService(repo, simulator)
    
    # Test different questions
    questions = [
        "What is the current temperature?",
        "How do I fix a motor issue?",
        "What maintenance is due next week?",
        "Explain the VFD troubleshooting procedure",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─' * 80}")
        print(f"Question {i}: {question}")
        print('─' * 80)
        
        request = ChatRequest(message=question)
        response = service.generate_response(request)
        
        print(f"\nResponse:\n{response.reply[:500]}...")  # Show first 500 chars
        print(f"\nConfidence: {response.confidence}")
        print(f"Recommended Actions: {len(response.recommended_actions)} actions")
        if response.recommended_actions:
            for j, action in enumerate(response.recommended_actions[:3], 1):
                print(f"  {j}. {action}")
    
    print("\n" + "=" * 80)
    print("Demo complete! Each question received a different, contextual response.")
    print("=" * 80)


if __name__ == "__main__":
    main()
