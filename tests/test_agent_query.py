from agent_setup import setup_agent

def test_specific_query():
    agent = setup_agent()
    
    # Test query
    query = "What is Boot Sequence without Boot Manager?"
    print(f"\nQuery: {query}")
    
    response = agent.query(query)
    print(f"\nResponse: {response}")

if __name__ == "__main__":
    test_specific_query()
