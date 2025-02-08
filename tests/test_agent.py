from agent_setup_improved import setup_agent

def test_agent():
    try:
        # Set up the agent
        print("Setting up agent...")
        agent = setup_agent()
        
        # Test query
        print("\nTesting agent with a simple query...")
        test_query = "What are the exact items included in the Flash Bootloader delivery? Please also include any notes about licensing requirements."
        
        print(f"Query: {test_query}")
        response = agent.chat(test_query)
        
        print("\nResponse:")
        print(response)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_agent()
