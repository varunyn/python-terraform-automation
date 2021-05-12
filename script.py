import fileinput
import oci
from oci.config import from_file
import io
import zipfile
import re
from oci.resource_manager.models import UpdateStackDetails, UpdateConfigSourceDetails, UpdateZipUploadConfigSourceDetails
import os
import shutil
import base64
import json
import shutil

path = os.path.dirname(__file__)
config = from_file()
rm_client = oci.resource_manager.ResourceManagerClient(config)
compartment_id = "ENTER COMPARTMENT OCID HERE "


def list_stacks():
    try:
        # Returns a list of all stacks in the current compartment
        getStacks = rm_client.list_stacks(
            compartment_id=compartment_id, lifecycle_state="ACTIVE")
        # Create a list that holds a list of the stack id
        stacks = [i.id for i in getStacks.data]
    except Exception as ex:
        print("ERROR: accessing Compute instances failed", ex)
        raise
    readStack(stacks)


def readStack(stacks):
    for stackId in stacks:
        count = 0
        shape = None
        ocpus = None
        memory = None
        try:

            stack = rm_client.get_stack(
                stack_id=stackId)

            stackConfig = rm_client.get_stack_tf_config(
                stack_id=stackId)

            getTfState = rm_client.get_stack_tf_state(
                stack_id=stackId)

            response = getTfState.data.json()

            for instances in response['resources']:
                if 'oci_core_instance' in instances['type']:
                    shape = instances['instances'][0]['attributes']['shape']
                    count += 1
                    if 'shape_config' in instances['instances'][0]['attributes']:
                        ocpus = instances['instances'][0]['attributes']['shape_config'][0]['ocpus']
                        memory = instances['instances'][0]['attributes']['shape_config'][0]['memory_in_gbs']
                    else:
                        print("shape_config is not found")

            if count > 0 and (shape != 'VM.Standard.E3.Flex' and shape != 'VM.Standard.E4.Flex'):

                shapeConfig = """
        shape_config {\n\
            memory_in_gbs = "%s"\n\
            ocpus         = "%s"\n\
        }\n\
        """ % (memory, ocpus)

            # Download Terraform cofig file from ORM Stack
                z = zipfile.ZipFile(io.BytesIO(stackConfig.data.content))
                z.extractall("rm_download")

            # Add shape_config in TF config
                tfConfigFilePath = os.path.join(path, "rm_download/main.tf")
                with open(tfConfigFilePath, 'r+') as f:
                    s = f.read()
                    new_s = re.sub(r'("VM.Standard[0-9a-z\.]+")',
                                   r'\1\n{}'.format(shapeConfig), s)
                    f.seek(0)
                    f.write(new_s)

            # Replace VM Shape to Flex
                with fileinput.input(tfConfigFilePath, inplace=True, backup='.bak') as file:
                    for line in file:
                        line = re.sub(
                            r'("VM.Standard[0-9a-z\.]+")', '"VM.Standard.E4.Flex"', line)
                        print(line)

            # Zip Config File
                shutil.make_archive(
                    'rm', 'zip', 'rm_download')

                zipfilePath = 'rm.zip'

                def create_base64encoded_zip(config_source):
                    if config_source.endswith(".zip") and os.path.isfile(config_source) and zipfile.is_zipfile(config_source):
                        with open(config_source, mode='rb') as zip_file:
                            return base64.b64encode(zip_file.read()).decode('utf-8')

                send_value = create_base64encoded_zip(zipfilePath)

            # Update ORM stack
                zipFileDetails = UpdateZipUploadConfigSourceDetails(
                    config_source_type='ZIP_UPLOAD', zip_file_base64_encoded=send_value)
                stackDetails = UpdateStackDetails(
                    config_source=zipFileDetails)
                updateStack = rm_client.update_stack(
                    stack_id=stackId, update_stack_details=stackDetails)

            # Run Job with Updated Stack
                if updateStack.data:
                    create_job_response = rm_client.create_job(
                        create_job_details=oci.resource_manager.models.CreateJobDetails(
                            stack_id=stackId,
                            display_name="newShapeJob",
                            operation="APPLY",
                            job_operation_details=oci.resource_manager.models.CreateApplyJobOperationDetails(
                                operation="APPLY",
                                execution_plan_strategy="AUTO_APPROVED")
                        ))
                    print(create_job_response.data)

                tfConfigFolderPath = os.path.join(path, "rm_download")
                shutil.rmtree(tfConfigFolderPath)
                tfConfigZipPath = os.path.join(path, "rm.zip")
                os.remove(tfConfigZipPath)

            else:
                pass

        except Exception as ex:
            print("ERROR: accessing Compute instances failed", ex)
            raise


list_stacks()
