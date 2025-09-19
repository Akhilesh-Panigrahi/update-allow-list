#python3
# This script updates an IP address allow list by removing addresses specified in a remove list.

# Define the list of IP addresses to be removed.
# This was mentioned in the document but not defined, so I've created a sample list.
remove_list = ["192.168.25.6", "192.168.25.14", "192.168.25.22"]

# Assign the filename of the allow list to a variable.
import_file = "allow_list.txt"

# Use a 'with' statement to open and read the file.
# This ensures the file is automatically closed even if errors occur.
with open(import_file, "r") as file:
    # Read the entire file content into a single string.
    ip_addresses = file.read()

# Convert the string of IP addresses into a list of individual IP addresses.
# The .split() method breaks the string apart by whitespace by default.
ip_addresses = ip_addresses.split()

# Iterate through each IP address in the remove_list.
for element in remove_list:
    # Check if the IP address from the remove list is currently in the allow list.
    if element in ip_addresses:
        # If it is, remove that IP address from the allow list.
        ip_addresses.remove(element)

# Join the elements of the updated list back into a single string.
# Each IP address will be separated by a newline character ("\n").
ip_addresses = "\n".join(ip_addresses)

# Open the original file in write mode ("w"), which overwrites its contents.
with open(import_file, "w") as file:
    # Write the updated string of IP addresses back into the file.
    file.write(ip_addresses)

# Optional: Print a confirmation message to the console.
print("Allow list has been updated successfully.")