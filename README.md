# Update Allow List

This project is a Python-based tool designed to update an "allow_list.txt" file by removing
specified IP addresses from it. The tool reads the file, processes the list of IPs, and writes
the updated list back to the file.

## Usage

Run the script via the command line with:

```bash
python update_allow_list.py --file allow_list.txt --remove 192.168.1.2 10.0.0.5

