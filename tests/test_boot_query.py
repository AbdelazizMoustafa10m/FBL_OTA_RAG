from agent_setup import setup_agent

def test_boot_queries():
    agent = setup_agent()
    
    # Test different boot-related queries
    queries = [
        "What happens during the boot process?",
        "Explain the boot sequence",
        "How does the bootloader work?",
        "What are the steps in booting?",
    ]
    
    for query in queries:
        print(f"\n\nQuery: {query}")
        response = agent.query(query)
        print(f"\nResponse: {response}")
        print("-" * 80)

if __name__ == "__main__":
    test_boot_queries()
