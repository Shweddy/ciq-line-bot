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

def run_cli():
    """Run a command-line interface for the CIQ bot."""
    print("CIQ Information Bot CLI")
    print("======================")
    print("Type an airport code (e.g., /KUL, /SIN, /HKG) or 'exit' to quit")
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip().upper()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if user_input.startswith('/'):
                airport_code = user_input[1:]
                response = format_ciq_info(airport_code)
                print("\n" + response)
            else:
                print("Please enter an airport code starting with '/' (e.g., /KUL)")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def list_available_airports():
    """List all available airport codes."""
    print("\nAvailable airport codes:")
    codes = list(ciq_data.keys())
    codes.sort()
    
    # Format in columns
    columns = 5
    for i in range(0, len(codes), columns):
        row = codes[i:i+columns]
        print("  ".join(f"{code}" for code in row))

if __name__ == "__main__":
    print("\nWelcome to the CIQ Information Bot!")
    list_available_airports()
    run_cli() 