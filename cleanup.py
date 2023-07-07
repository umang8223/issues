#!/usr/bin/python


# cleanup.py
#   - Get the packages based on the bucket_name and release.
#   - Calculates the current timestamp and for the oldest package, based on that checks SUPPORT_WINDOW.
#   - Get all the latest release based on the tag.
#   - Delete the packages which does not have the latest tag.
#
# Parameters : 
#   bucket_name,        # Chdev, chibmsigned or chscan
#   release,            # any parameter can be passed based on release. ex: 23.1,23.2
#

from datetime import datetime
import getopt
import os
import re
import subprocess
import sys

def get_filtered_packages(bucket_name, release):
    # Filter the list of objects that match the pattern
    package_list_output = subprocess.check_output(f'ibmcloud cos objects --bucket {bucket_name}', shell=True)
    package_list_str = package_list_output.decode('utf-8')
    if bucket_name == "chscan":
        filtered_packages = [package for package in package_list_str.strip().split("\n") if re.search(rf"\b{release}\.\d+\.\d+-\d+\b", package)]
    else:
        filtered_packages = [package for package in package_list_str.strip().split("\n") if re.search(rf"clickhouse.*{release}\.[0-9]", package)]
    for package in filtered_packages:
        print(package)
    # print(filtered_packages[0])
    return filtered_packages

def extract_package_details(filtered_packages):
    # Extract the package name and upload date from the package list
    package_details = []
    for package in filtered_packages:
        fields = package.split()
        if len(fields) >= 5:
            package_name = fields[0]
            timestamp_str = " ".join(fields[1:4]) + " " + fields[5]
            try:
                date_obj = datetime.strptime(timestamp_str, "%b %d, %Y %H:%M:%S")
                package_details.append((package_name, date_obj))
            except ValueError:
                pass
    return package_details

def get_oldest_package(package_details, release):
    # Sort the package details based on the upload date and print the first package name
    if package_details:
        sorted_packages = sorted(package_details, key=lambda x: x[1])
        oldest_package = sorted_packages[0][0]
        oldest_timestamp = sorted_packages[0][1].strftime("%b %d, %Y %H:%M:%S")
        print(f"The first package uploaded for release {release} is {oldest_package}, uploaded on {oldest_timestamp}")
    else:
        print(f"No packages found for release {release}")
        return None, None
    return oldest_package, oldest_timestamp

def calculate_timestamps(oldest_timestamp):
    # Time in seconds
    oldest_timestamp_obj = datetime.strptime(oldest_timestamp, "%b %d, %Y %H:%M:%S")
    oldest_timestamp_sec = int(oldest_timestamp_obj.timestamp())
    print("Oldest timestamp in seconds: ", oldest_timestamp_sec)
    print(f"The oldest package was uploaded on {oldest_timestamp} ({oldest_timestamp_sec:.0f})")

    current_timestamp_sec = int(datetime.now().timestamp())
    print("Current timestamp in seconds: ",current_timestamp_sec)
    return oldest_timestamp_sec, current_timestamp_sec

def determine_support_window(filtered_packages):
    if 'stable' in filtered_packages:
        print("Stable version, 3 months supports window") 
        # Set the time period for which packages will be kept (in seconds)
        SUPPORT_WINDOW = 90 * 24 * 60 * 60
    else:
        print("lts version, 1 year supports window")
        # Set the time period for which packages will be kept (in seconds)
        SUPPORT_WINDOW = 365 * 24 * 60 * 60
    return SUPPORT_WINDOW

def get_latest_release(filtered_packages, bucket_name, release):

    if bucket_name == "chscan":
        pattern = f"va-scan-report.*{release}.*ibm\\.json"
        filtered_reports = []
        for package in filtered_packages:
            if re.match(pattern, package):
                filtered_reports.append(package)
    else:
        pattern = f"clickhouse.*{release}.*amd64.deb"
        filtered_reports = []
        for package in filtered_packages:
            print(package)
            if re.match(pattern, package):
                filtered_reports.append(package)

    filtered_dates = []
    for package in filtered_reports:
        fields = package.split()
        package_date_str = " ".join(fields[1:4]) + " " + fields[5]
        package_date = datetime.strptime(package_date_str, '%b %d, %Y %H:%M:%S')
        filtered_dates.append(package_date)

    if filtered_dates:
        latest_date = max(filtered_dates)
        latest_date_converted = latest_date.strftime('%b %d, %Y at %H:%M:%S')
        print("Latest date: ", latest_date_converted)
        return find_package_by_date(filtered_reports, latest_date_converted, filtered_packages, bucket_name)
    return None

def find_package_by_date(package_list, latest_date, filtered_packages, bucket_name):
    """
    Find a package by date.
    """
    date_pattern = r'^[a-zA-Z]{3} \d{1,2}, \d{4} at \d{1,2}:\d{2}:\d{2}$'
    if not re.match(date_pattern, latest_date):
        raise ValueError('Invalid date format')
    
    if bucket_name == "chscan":
        for package in package_list:
            if latest_date in package:
                print(f"Package {package} found for date {latest_date}")
                latest_release_tag = '-'.join(package.split('-')[3:5])
                print('Latest release tag:', latest_release_tag)
    else:
        for package in package_list:
            if latest_date in package:
                print(f"Package {package} found for date {latest_date}")
                latest_release_tag = package.split('_')[1].split('-')[0]
                print('Latest release tag:', latest_release_tag)
    return list_latest_releases(latest_release_tag, filtered_packages, bucket_name)

def list_latest_releases(latest_release_tag, filtered_packages, bucket_name):

    list_of_latest_releases = []
    for package in filtered_packages:
        if latest_release_tag in package:
            list_of_latest_releases.append(package)

    print("List of latest releases:")
    for package in list_of_latest_releases:
        print(package)

    print("check if latest_release_packages = filtered_packages")
    number_of_release_packages = len(list_of_latest_releases)
    number_of_total_packages = len(filtered_packages)

    if number_of_total_packages == number_of_release_packages:
        print("All packages have the latest release tag. Exiting.")
    else:
        print("Packages need to be deleted.")
    return delete_packages(bucket_name, latest_release_tag, filtered_packages)

def delete_packages(bucket_name, latest_release_tag, packages):
    """
    Delete packages.
    """
    packages_to_be_deleted = [package for package in packages if latest_release_tag not in package]
    print('Packages to be deleted:\n')
    for package in packages_to_be_deleted:
        print(package)

    # Deleting PACKAGES as it's not under support window
    for package in packages_to_be_deleted:
        package_name = package.split()[0]
        print(package_name)
        os.system(f"ibmcloud cos delete-object --bucket {bucket_name} --key {package_name} --force")
    return packages_to_be_deleted

def main():
    # Default values for bucket_name and release
    bucket_name = None
    release = None
    
    # Parsing command-line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:r:", ["help", "bucket=", "release="])
    except getopt.GetoptError:
        print(f"Usage: {sys.argv[0]} -b <bucket_name> -r <release>")
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(f"Usage: {sys.argv[0]} -b <bucket_name> -r <release>")
            sys.exit()
        elif opt in ("-b", "--bucket"):
            bucket_name = arg
        elif opt in ("-r", "--release"):
            release = arg

    if not bucket_name or not release:
        print(f"Usage: {sys.argv[0]} -b <bucket_name> -r <release>")
        sys.exit(1)

    # Getting packages from bucket
    filtered_packages = get_filtered_packages(bucket_name, release)
    package_details = extract_package_details(filtered_packages)
    oldest_package, oldest_timestamp = get_oldest_package(package_details, release)
    oldest_timestamp_sec, current_timestamp_sec = calculate_timestamps(oldest_timestamp)
    # checking for SUPPORT_WINDOW duration    
    SUPPORT_WINDOW = determine_support_window(oldest_package)

    print("Checking if it is under support window")
    if current_timestamp_sec - oldest_timestamp_sec > SUPPORT_WINDOW:
        print(f"Support period for release {release} has ended, Delete the packages")

        get_latest_release(filtered_packages, bucket_name, release)
         
    else:
        print(f"Support period for release {release} is still active")
if __name__ == "__main__":
    main()
