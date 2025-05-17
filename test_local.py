from ciq_data import ciq_data

def format_ciq_info(airport_code):
    """Format CIQ information for a given airport code."""
    if airport_code not in ciq_data:
        return f"Sorry, I don't have information for airport code {airport_code}."
    
    info = ciq_data[airport_code]
    response = f"CIQ Information for {airport_code}:\n\n"
    
    for key, value in info.items():
        # Format the key to be more readable
        formatted_key = key.replace('_', ' ').title()
        response += f"{formatted_key}: {value}\n"
    
    return response

def test_bot():
    """Test the CIQ bot locally without Line API integration."""
    print("CIQ Line Bot Tester")
    print("==================")
    print("Type an airport code (e.g., KUL, SIN, HKG) or 'exit' to quit")
    
    while True:
        user_input = input("\nEnter command (e.g., /KUL): ").strip().upper()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        if user_input.startswith('/'):
            airport_code = user_input[1:]
            response = format_ciq_info(airport_code)
            print("\n" + response)
        else:
            print("Please enter an airport code starting with '/' (e.g., /KUL)")

if __name__ == "__main__":
    test_bot() 