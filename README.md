# OCI Terraform Stack VM Shape Migration Tool

## Overview

This Python automation script migrates Oracle Cloud Infrastructure (OCI) compute instances from legacy fixed VM shapes to modern flexible VM shapes (`VM.Standard.E4.Flex`) using OCI Resource Manager (ORM). The script automatically updates Terraform configurations and applies changes across all active stacks in a specified compartment.

## Features

- **Automated Discovery**: Scans all active ORM stacks in a compartment
- **Smart Migration**: Only migrates instances using non-flexible VM shapes
- **Configuration Preservation**: Maintains existing memory and OCPU allocations
- **Terraform Integration**: Downloads, modifies, and re-uploads Terraform configurations
- **Auto-Apply**: Automatically executes Terraform apply jobs with approval
- **Cleanup**: Removes temporary files after processing

## What It Does

1. Lists all active ORM stacks in the specified compartment
2. Analyzes each stack's Terraform state for compute instances
3. Identifies instances using legacy VM shapes (excludes `VM.Standard.E3.Flex` and `VM.Standard.E4.Flex`)
4. Downloads and modifies Terraform configuration files:
   - Adds `shape_config` blocks with current resource specifications
   - Updates VM shape to `VM.Standard.E4.Flex`
5. Updates the ORM stack with modified configuration
6. Executes Terraform apply job automatically

## Prerequisites

- Python 3.6 or higher
- OCI CLI configured with valid credentials
- OCI Python SDK
- Appropriate IAM permissions:
  - `manage` permissions on Resource Manager stacks
  - `read` permissions on compute instances
  - `use` permissions on the target compartment

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repository-url>
cd python-terraform-automation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements
```

### 4. Configure OCI

Ensure your OCI configuration file (`~/.oci/config`) is properly set up:

```ini
[DEFAULT]
user=ocid1.user.oc1..your-user-ocid
fingerprint=your-fingerprint
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..your-tenancy-ocid
region=your-region
```

### 5. Update Script Configuration

Open `script.py` and modify line 17 to enter your compartment OCID:

```python
compartment_id = "ocid1.compartment.oc1..your-compartment-ocid"
```

## Usage

### Run the Migration Script

```bash
python script.py
```

The script will:

- Automatically discover all active stacks
- Process each stack that contains legacy VM shapes
- Display progress and job information
- Clean up temporary files

### Monitoring Progress

- Check OCI Console → Resource Manager → Jobs to monitor apply job progress
- Review job logs for detailed execution information

## Important Notes

### ⚠️ Disclaimer

- **DO NOT use this script in production environments without thorough testing**
- Test in development/staging environments first
- Review all Terraform changes before applying to critical workloads
- Ensure you have proper backups and rollback procedures

### Supported VM Shapes

- **Source**: Any legacy fixed VM shapes (e.g., `VM.Standard2.1`, `VM.Standard2.2`, etc.)
- **Target**: `VM.Standard.E4.Flex` (flexible shape)
- **Preserved**: Existing `VM.Standard.E3.Flex` and `VM.Standard.E4.Flex` instances

### Limitations

- Only processes `oci_core_instance` resources
- Requires instances to have `shape_config` attributes
- Assumes Terraform configuration is in `main.tf`

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify OCI configuration and permissions
2. **Compartment Access**: Ensure correct compartment OCID and access rights
3. **Missing Dependencies**: Run `pip install -r requirements` again
4. **Terraform Errors**: Check ORM job logs in OCI Console

### Error Handling

The script includes basic error handling and will display error messages for:

- OCI API access issues
- Terraform configuration problems
- File system operations

## File Structure

```
python-terraform-automation/
├── README.md           # This documentation
├── requirements        # Python dependencies
├── script.py          # Main migration script
└── .git/              # Git repository data
```

## Contributing

1. Test thoroughly in non-production environments
2. Follow existing code style and error handling patterns
3. Update documentation for any new features
4. Consider adding logging and more granular error handling

## License

Use at your own risk. This tool is provided as-is for reference purposes.
