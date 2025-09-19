# IP Address Allow List Updater
### Project Description
This project provides a Python script that automates the process of updating a file-based IP address allow list. It reads a list of approved IP addresses from allow_list.txt and removes any addresses that are specified in a remove_list within the script. This is useful for managing access to restricted content or services where access control is handled through an IP allow list.

### How It Works
The script executes the following steps:

  1. Reads the Allow List: It opens and reads all the IP addresses from the allow_list.txt file.
  2. Processes the Remove List: It iterates through a hardcoded Python list of IP addresses (remove_list) that need to be removed.
  3. Removes Matching IPs: For each IP address in the remove_list, the script checks if it exists in the current allow list. If a match is found, the IP address is removed.
  4. Updates the File: After removing all specified addresses, the script overwrites the original allow_list.txt file with the updated, cleaned list of IP addresses. Each IP address is written on a new line.

### Usage
To use this script, follow these steps:

  1. Clone the repository or download the files.
  2. Make sure you have update_allow_list.py and allow_list.txt in the same directory.
  3. Populate your allow list: Add the IP addresses you want to grant access to in the allow_list.txt file, with each IP on a new line.
  4. Define the remove list: Open the update_allow_list.py script and modify the remove_list variable to include the IP addresses you wish to revoke access for.
 
```
# Define the list of IP addresses to be removed.
remove_list = ["192.168.25.6", "192.168.25.14", "192.168.25.22"]
```
  5. Run the script from your terminal:
```
python update_allow_list.py
```
  6. After the script runs, the allow_list.txt file will be automatically updated.

### Files in this Repository
- update_allow_list.py: The main Python script that performs the update logic.
- allow_list.txt: A sample text file containing the list of allowed IP addresses.
