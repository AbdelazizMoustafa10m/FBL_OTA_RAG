from agent_setup import setup_agent

def test_boot_query():
    # Initialize the agent with our improved settings
    agent = setup_agent()
    
    print("Testing improved agent with boot sequence query...\n")
    
    # Test the query
    query = "what is Boot Sequence without Boot Manager"
    print(f"Query: {query}\n")
    
    # Get response
    response = agent.query(query)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_boot_query()
