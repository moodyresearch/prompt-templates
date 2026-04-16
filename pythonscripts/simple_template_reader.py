import re
import urllib.request
import os
from typing import Dict, List


def get_raw_github_url(github_url: str) -> str:
    """
    Convert a standard GitHub URL to a raw content URL.
    
    Examples:
        https://github.com/user/repo/blob/main/file.txt
        -> https://raw.githubusercontent.com/user/repo/main/file.txt
    """
    # Handle both github.com and raw.githubusercontent.com URLs
    if "raw.githubusercontent.com" in github_url:
        return github_url
    
    # Convert standard GitHub URL to raw URL
    github_url = github_url.replace("github.com", "raw.githubusercontent.com")
    github_url = github_url.replace("/blob/", "/")
    return github_url


def is_github_url(path: str) -> bool:
    """
    Check if the input is a GitHub URL or a local file path.
    
    Args:
        path: The input string to check
        
    Returns:
        True if it's a GitHub URL, False if it's a local file path
    """
    return path.startswith("http://") or path.startswith("https://")


def fetch_template(source: str) -> str:
    """
    Fetch the template content from either a GitHub URL or a local file.
    
    Args:
        source: GitHub URL or local file path to the template
        
    Returns:
        The content of the template file
        
    Raises:
        Exception: If the source cannot be accessed
    """
    if is_github_url(source):
        # Fetch from GitHub
        raw_url = get_raw_github_url(source)
        try:
            with urllib.request.urlopen(raw_url) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to fetch template from {raw_url}: {str(e)}")
    else:
        # Read from local file
        try:
            if not os.path.exists(source):
                raise FileNotFoundError(f"File not found: {source}")
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Failed to read template from {source}: {str(e)}")


def extract_placeholders(template: str) -> List[str]:
    """
    Extract placeholder names from the template.
    Placeholders are identified by text within curly braces: {placeholder_name}
    
    Args:
        template: The template string
        
    Returns:
        A list of unique placeholder names (without the curly braces)
    """
    # Find all placeholders in the format {name}
    matches = re.findall(r'\{([^}]+)\}', template)
    # Return unique placeholders in order of appearance
    seen = set()
    unique_matches = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            unique_matches.append(match)
    return unique_matches


def prompt_for_values(placeholders: List[str]) -> Dict[str, str]:
    """
    Prompt the user for values for each placeholder.
    
    Args:
        placeholders: List of placeholder names
        
    Returns:
        Dictionary mapping placeholder names to user-provided values
    """
    values = {}
    print("\n" + "="*50)
    print("Enter values for the following placeholders:")
    print("="*50 + "\n")
    
    for placeholder in placeholders:
        while True:
            value = input(f"Enter value for '{placeholder}': ").strip()
            if value:  # Ensure non-empty input
                values[placeholder] = value
                break
            else:
                print("  ⚠️  Value cannot be empty. Please try again.")
    
    return values


def fill_template(template: str, values: Dict[str, str]) -> str:
    """
    Fill the template with the provided values.
    
    Args:
        template: The template string
        values: Dictionary mapping placeholder names to their values
        
    Returns:
        The filled template
    """
    filled = template
    for placeholder, value in values.items():
        filled = filled.replace(f"{{{placeholder}}}", value)
    return filled


def main():
    """Main function to run the prompt template filler."""
    print("GitHub Prompt Template Filler")
    print("=" * 50)
    
    # Get the source from user (GitHub URL or local file path)
    source = input("\nEnter a GitHub URL or local file path to the prompt template: ").strip()
    
    if not source:
        print("Error: Source cannot be empty.")
        return
    
    try:
        # Fetch the template
        print("\nFetching template...")
        template = fetch_template(source)
        
        # Extract placeholders
        placeholders = extract_placeholders(template)
        
        if not placeholders:
            print("\nNo placeholders found in the template.")
            print("\nTemplate content:")
            print("-" * 50)
            print(template)
            print("-" * 50)
            return
        
        # Prompt for values
        values = prompt_for_values(placeholders)
        
        # Fill the template
        filled_template = fill_template(template, values)
        
        # Display the result
        print("\n" + "="*50)
        print("Filled Template:")
        print("="*50)
        print(filled_template)
        print("="*50)
        
        # Optional: Save to file
        save_option = input("\nSave to file? (y/n): ").strip().lower()
        if save_option == 'y':
            filename = input("Enter filename (default: 'filled_prompt.txt'): ").strip()
            if not filename:
                filename = "filled_prompt.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(filled_template)
            print(f"✓ Saved to {filename}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
