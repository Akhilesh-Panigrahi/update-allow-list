#python3

import argparse

def update_allow_list(file_path, remove_list):
    """
    Update the allow list file by removing IP addresses specified in remove_list.

    Parameters:
        file_path (str): Path to the "allow_list.txt" file.
        remove_list (list of str): List of IP addresses to be removed.
    """
    try:
        # Open the file to read its contents
        with open(file_path, "r") as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    # Convert the file content (string) into a list of IP addresses
    ip_addresses = data.split()

    # Iterate through the remove list and remove matching IP addresses
    for ip in remove_list:
        if ip in ip_addresses:
            ip_addresses.remove(ip)

    # Convert the updated list back to a string with each IP on a new line
    updated_data = "\n".join(ip_addresses)

    # Write the updated data back to the same file (overwriting it)
    with open(file_path, "w") as file:
        file.write(updated_data)

    print("The allow list has been updated successfully.")

def main():
    parser = argparse.ArgumentParser(
        description="Update an IP allow list file by removing specified IP addresses."
    )
    parser.add_argument(
        "--file", 
        type=str, 
        default="allow_list.txt", 
        help="Path to the allow list file (default: allow_list.txt)"
    )
    parser.add_argument(
        "--remove", 
        nargs='+', 
        required=True, 
        help="List of IP addresses to remove from the allow list (e.g., --remove 192.168.1.2 10.0.0.5)"
    )
    args = parser.parse_args()

    update_allow_list(args.file, args.remove)

if __name__ == "__main__":
    main()
