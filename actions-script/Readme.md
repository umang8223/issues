## create_vm_runner.py

This script is used to create a Fyre VM and install a self-hosted runner for GitHub Actions on the VM. It performs the following steps:

1. Create a Fyre VM using a curl command.
2. SSH into the root user of the VM, and add a new user.
3. SSH into the new user of the VM, install dependencies.
4. Get the latest release version of the runner and retrieve the access token for the installation of the runner.
5. Install the self-hosted runner on the VM and start it.

### Prerequisites

Before running the script, ensure that you have the following information and dependencies:

- Python (version 3 or higher) installed on the system.
- `paramiko`, `requests`, and `subprocess` Python libraries installed. You can install them using `pip install paramiko requests`.
- Access to the Fyre API and GitHub API with the necessary credentials.
- SSH public key for authentication.
- Username and API key for accessing the Fyre API.
- The desired number of CPUs, memory, and operating system flavor for the VM.
- The owner or organization name of the GitHub repository.
- The name of the GitHub repository.
- An access token or authentication token used for GitHub API operations.
- Labels to be associated with the self-hosted runner for GitHub Actions.

### Usage

To run the script, use the following command:

```
python create_vm_runner.py fyre_username fyre_apikey cpu memory os_version labels ssh_public_key_path platform vault_token token
```
Replace the placeholders with the appropriate values for your environment.

### Script Flow
The script follows these steps:

* Read the necessary parameters from the command-line arguments.
* Generate a custom UUID for the VM.
* Create a runner VM using the Fyre API by executing a curl command.
* SSH into the root user of the VM, and create a new user.
* SSH into the new user of the VM, install dependencies.
* Get the latest release version of the runner from the GitHub API.
* Get the access token for the repository to install the self-hosted runner.
* Create a folder for the actions runner on the remote VM and download the latest runner package.
* Extract the installer and configure the runner using the provided access token and other parameters.
* The runner creation process is complete.

### Script Parameters

The script requires the following parameters to be provided as command-line arguments:

* fyre_username: The username for accessing the Fyre API.
* fyre_apikey: The API key for accessing the Fyre API.
* cpu: The number of CPUs assigned to the virtual machine.
* memory: The amount of memory (in GB) assigned to the virtual machine.
* os_version: The flavor or version of the operating system for the virtual machine.
* labels: Labels to be associated with the self-hosted runner for GitHub Actions.
* ssh_public_key_path: The file path of the SSH public key used for authentication.
* platform: Platform for the VM.
* vault_token: Token for vault
* token: Token for ClibMouse

### Example
Here is an example of running the script:
```
python create_vm_runner.py my_fyre_username my_fyre_apikey 2 16 "ubuntu 22.04" "first,second,third" /path/to/ssh_public_key.pub x vault_token token
```

Replace the placeholders with your actual values.
