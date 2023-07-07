#!/usr/bin/python


# auto_release_page.py
#   - Preapare package and images based on the parameters passed to this pipeline
#   - If condition: checks if it is a incremental or brand new release
#   - If its brand new release then, it check for the filename in the directory
#   - Creates new empty mdx file in the directory
#   - Add title and the main portion of the release
#   - Push the new mdx file


# Parameters : 
#   branch,                   # ex:"v23.4.1.1943-stable-ibm"
#   version_patch,            # This parameter refers to a specific patch or update within a given branch.
#   release_type,             # Type of release, lts or Stable
#
#


from datetime import datetime
import os
import sys
import subprocess

directory = "/artifacts/release-repo"   # used for push to repo
directory_pages= "/artifacts/release-repo/src/pages/clickhouse-server-releases/"    # used during the addition or checking the .mdx file
directory_data= "/artifacts/release-repo/src/data/"   # used to update the nav-items.yaml
TITLE_TEMPLATE_FILE = "title_block_template"
MAIN_TEMPLATE_FILE = "main_template"
dropdown_filename = "nav-items.yaml"


def preparaing_packages(branch,release_type):

    RELEASE = branch[1:]
    print('Release :',RELEASE)

    RELEASE_BRANCH= ".".join(RELEASE.split(".")[:2])
    print("Release branch:", RELEASE_BRANCH)

    RELEASE_TAG = RELEASE.split("-")[0]
    print("Release tag:", RELEASE_TAG)

    if release_type == "stable":
        SUPPORT_WINDOW = "3 months"
        SUPPORT_WINDOW_SEC = 90 * 24 * 60 * 60
    else:
        SUPPORT_WINDOW = "1 year"
        SUPPORT_WINDOW_SEC = 365 * 24 * 60 * 60        
    print('Support window :',SUPPORT_WINDOW)
    # print('Support window in seconds: ', SUPPORT_WINDOW_SEC)

    # Todays date
    TIMESTAMP = datetime.today() # output full timestamp 2023-05-03 10:16:36
    # print(TIMESTAMP)
    RELEASE_DATE = TIMESTAMP.strftime("%Y-%m-%d") # output in this format 2023-05-03
    print('Release date :',RELEASE_DATE)

    # Release date in seconds
    RELEASE_DATE_SEC = int(datetime.now().timestamp())
    # print(RELEASE_DATE_SEC)

    # Release end date in sec
    RELEASE_END_SEC = RELEASE_DATE_SEC + SUPPORT_WINDOW_SEC
    # print(RELEASE_END_SEC)

    # Release end date in %Y-%m-%d
    date_time = datetime.fromtimestamp(RELEASE_END_SEC)
    RELEASE_END_DATE = date_time.strftime("%Y-%m-%d")
    print('Release end date :',RELEASE_END_DATE)

    RELEASE_TAG_RPM = RELEASE.replace("-", "_")

    # Assets
    print("Clickhouse-packages:")
    RPM_FILE_PPC64LE= f"clickhouse-{RELEASE_TAG_RPM}-1.ppc64le.rpm"
    print("Power RPM package:", RPM_FILE_PPC64LE)
    RPM_FILE_PPC64LE_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-rpm-local/{RPM_FILE_PPC64LE}"
    print("Power RPM package URL:",RPM_FILE_PPC64LE_URL)

    RPM_FILE_x86= f"clickhouse-{RELEASE_TAG_RPM}-1.x86_64.rpm"
    print("x86 RPM package:", RPM_FILE_x86)
    RPM_FILE_x86_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-rpm-local/{RPM_FILE_x86}"
    print("x86 RPM package URL:", RPM_FILE_x86_URL)

    DEB_FILE_AMD64= f"clickhouse_{RELEASE}_amd64.deb"
    print("AMD64 DEB package:", DEB_FILE_AMD64)
    DEB_FILE_AMD64_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-debian-local/{DEB_FILE_AMD64}"
    print("AMD64 DEB package URL:", DEB_FILE_AMD64_URL)

    DEB_FILE_PPC64LE= f"clickhouse_{RELEASE}_ppc64le.deb"
    print("Power DEB package:", DEB_FILE_PPC64LE)
    DEB_FILE_PPC64LE_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-debian-local/{DEB_FILE_PPC64LE}"
    print("Power DEB package URL:", DEB_FILE_PPC64LE_URL)


    #####
    print("Clickhouse-openssl-packages:")
    OPENSSL_RPM_FILE_PPC64LE= f"clickhouse-openssl-{RELEASE_TAG_RPM}-1.ppc64le.rpm"
    print("Openssl Power RPM package:", OPENSSL_RPM_FILE_PPC64LE)
    OPENSSL_RPM_FILE_PPC64LE_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-rpm-local/{OPENSSL_RPM_FILE_PPC64LE}"
    print("Openssl Power RPM package URL:",OPENSSL_RPM_FILE_PPC64LE_URL)

    OPENSSL_RPM_FILE_x86= f"clickhouse-openssl-{RELEASE_TAG_RPM}-1.x86_64.rpm"
    print("Openssl x86 RPM package:", OPENSSL_RPM_FILE_x86)
    OPENSSL_RPM_FILE_x86_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-rpm-local/{OPENSSL_RPM_FILE_x86}"
    print("Openssl x86 RPM package URL:", OPENSSL_RPM_FILE_x86_URL)

    OPENSSL_DEB_FILE_AMD64= f"clickhouse-openssl_{RELEASE}_amd64.deb"
    print("Openssl AMD64 DEB package:", OPENSSL_DEB_FILE_AMD64)
    OPENSSL_DEB_FILE_AMD64_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-debian-local/{OPENSSL_DEB_FILE_AMD64}"
    print("Openssl AMD64 DEB package URL:", OPENSSL_DEB_FILE_AMD64_URL)

    OPENSSL_DEB_FILE_PPC64LE= f"clickhouse-openssl_{RELEASE}_ppc64le.deb"
    print("Openssl Power DEB package:", OPENSSL_DEB_FILE_PPC64LE)
    OPENSSL_DEB_FILE_PPC64LE_URL=f"https://na.artifactory.swg-devops.com/artifactory/hyc-clickhouse-team-debian-local/{OPENSSL_DEB_FILE_PPC64LE}"
    print("Openssl Power DEB package URL:", OPENSSL_DEB_FILE_PPC64LE_URL)

    # print("Clickhouse-Docker-image")
    DOCKER_IMAGE_CLICKHOUSE=f"icr.io/clickhouse/clickhouse:{RELEASE}"
    print("Docker Image Clickhouse:", DOCKER_IMAGE_CLICKHOUSE)

    # print("Clickhouse-openssl-Docker-image")
    DOCKER_IMAGE_OPENSSL=f"icr.io/clickhouseclickhouse-openssl:{RELEASE}"
    print("Docker Image Clickhouse-Openssl:", DOCKER_IMAGE_OPENSSL)

    return RELEASE_BRANCH, SUPPORT_WINDOW, RELEASE_END_DATE, RELEASE_TAG, RELEASE_DATE

def check_mdx_file_exist_in_dir(branch, directory):
 
    print(branch)
    filename = branch + ".mdx"
    print(filename)
    # print(directory)

    file_path = os.path.join(directory, filename)
    if os.path.exists(file_path):
        print(f"{filename} exists in {directory}")
    else:
        print(f"{filename} doesn't exist in {directory}")
        print(f"Creating a new mdx file for release {branch}")
        create_new_release_file_mdx(filename, directory)
    return filename
    
def create_new_release_file_mdx(filename, directory):
    print(f"Creating a new mdx file for {filename}")
    print(directory)
    open(os.path.join(directory, f"{filename}"), "w").close()
    print(f"{filename} is created")
    # print(os.listdir(directory))
    file_list = os.listdir(directory)
    print(f"List of files in {directory}")
    for file in file_list:
        print(file)
    
    return filename

def prepare_title_main_template(title_template_file, directory, release_branch, SUPPORT_WINDOW, RELEASE_END_DATE, release_type, filename, main_template_file, RELEASE_TAG, RELEASE_DATE):

    print("Checking for title block template")
    print(filename)
    file_path = os.path.join(title_template_file, directory)
    if os.path.exists(file_path):
        print(f"{title_template_file} exists in {directory}")

        print("release_branch_test",release_branch)
        print("release_type_test",release_type)
        print("support window test", SUPPORT_WINDOW)
        print("release end date", RELEASE_END_DATE)        

        # PREPARE TITLE TEMPLATE
        with open(title_template_file, "r") as file:
            content = file.read()
            content = content.replace("RELEASE_BRANCH", release_branch)
            content = content.replace("RELEASE_TYPE", release_type)
            content = content.replace("SUPPORT_WINDOW", SUPPORT_WINDOW)
            content = content.replace("RELEASE_END_DATE", RELEASE_END_DATE)
            # file.seek(0)
            # file.write(content)
            print(content)
            print(filename)
        with open(filename, "a") as file:
            file.write(content)

    print("Checking for main block template")
    file_path = os.path.join(main_template_file, directory)
    if os.path.exists(file_path):
        print(f"{main_template_file} exists in {directory}")

        print("release_branch_test",RELEASE_TAG)
        print("release_type_test",RELEASE_DATE)          

        # PREPARE MAIN TEMPLATE
        with open(main_template_file, "r") as file:
            main_content = file.read()
            main_content = main_content.replace("RELEASE_TAG", RELEASE_TAG)
            main_content = main_content.replace("RELEASE_DATE", RELEASE_DATE)
            # file.seek(0)
            # file.write(content)
            print(main_content)
            print(filename)
        with open(filename, "a") as file:
            file.write("\n" + main_content)

def Update_nav_items(release_type, branch, directory, dropdown_filename):

    file_path = os.path.join(directory, dropdown_filename)
    if os.path.exists(file_path):
        print(f"{dropdown_filename} exists in {directory}")

        # Read the contents of the dropdown file
        with open(file_path, 'r') as file:
            dropdown_content = file.read()

        # Define the new content to add
        new_content = f'''- title: Clickhouse Server Releases
  pages:
    - title: {branch} ({release_type})
      path: /clickhouse-server-releases/{branch}'''

        # Replace the specified line with the new content
        new_dropdown_content = dropdown_content.replace('- title: Clickhouse Server Releases\n  pages:', new_content)

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(new_dropdown_content)
            print("Updated dropdown file.")
            print("Updated nav-items.yaml: \n", new_dropdown_content)
    else:
        print(f"{dropdown_filename} doesn't exist in {directory}")
        sys.exit(1)

def push_mdx(directory, filename, dropdown_filename):

    os.chdir(directory)
    print(os.getcwd())  # Print the current working directory

    subprocess.run(['ls', '-la'])

    subprocess.run(['git', 'stash'])
    subprocess.run(['git', 'pull'])
    subprocess.run(['git', 'stash', 'apply'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f"Added {filename} and Updated {dropdown_filename}"])
    subprocess.run(['git', 'push'])

def main():

    branch = sys.argv[1]
    version_patch = sys.argv[2]    
    release_type = sys.argv[3]

    print(branch)
    print(version_patch)
    print(release_type)

    RELEASE_BRANCH, SUPPORT_WINDOW, RELEASE_END_DATE, RELEASE_TAG, RELEASE_DATE = preparaing_packages(branch,release_type)

    # Checking for type of release
    if version_patch == "1":
        print("Its a Brand new release")

        print(RELEASE_BRANCH)

        filename = check_mdx_file_exist_in_dir(RELEASE_BRANCH, directory_pages)
        prepare_title_main_template(TITLE_TEMPLATE_FILE, directory_pages, RELEASE_BRANCH, SUPPORT_WINDOW, RELEASE_END_DATE, release_type, filename, MAIN_TEMPLATE_FILE, RELEASE_TAG, RELEASE_DATE)
        Update_nav_items(release_type, RELEASE_BRANCH, directory_data, dropdown_filename)
        push_mdx(directory, filename, dropdown_filename)

    else:
        print("Its a Incremental release")


if __name__ == "__main__":
    main()
