# Backup and delete all volumes in all regions with tag Backup=True

import boto3
import datetime
import ast

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    # Get list of regions
    regions = ec2.describe_regions().get('Regions',[] )

    # Iterate over regions
    for region in regions:
        print "Checking region %s " % region['RegionName']
        reg=region['RegionName']

        # Connect to region
        ec2 = boto3.client('ec2', region_name=reg)
        
        # Delete Snapshots with date DeleteOn=Today
        delete_today = datetime.date.today().strftime('%Y-%m-%d')
        snapshot_response = ec2.describe_snapshots( Filters=[{'Name': 'tag-key', 'Values': ['DeleteOn']},{'Name': 'tag-value', 'Values': [delete_today]}])
        
        for snap in snapshot_response['Snapshots']:
            print "Deleting snapshot %s in region %s" % (snap['SnapshotId'], region['RegionName'])
            ec2.delete_snapshot(SnapshotId=snap['SnapshotId'])
    
        # Get all volumes with tag Backup=True  
        result = ec2.describe_volumes( Filters=[{'Name': 'tag-value', 'Values': ['Backup', 'True']}])
        
        for volume in result['Volumes']:
            if 'Tags' in volume:
                for tags in volume['Tags']:
                    if tags['Key'] == 'Retention':
                        ret_days = tags["Value"]
                        ret_days = ast.literal_eval(ret_days)
                        delete_on = (datetime.date.today() + datetime.timedelta(ret_days)).strftime('%Y-%m-%d')
            print "Backing up %s in %s" % (volume['VolumeId'], volume['AvailabilityZone'])
        
            # Create snapshot
            result = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description='Created by Lambda backup function ebs-snapshots')
        
            # Get snapshot resource 
            ec2resource = boto3.resource('ec2', region_name=reg)
            snapshot = ec2resource.Snapshot(result['SnapshotId'])
        
            volumename = 'N/A'
        
            # Find name tag for volume if it exists
            if 'Tags' in volume:
                for tags in volume['Tags']:
                    if tags["Key"] == 'Name':
                        volumename = tags["Value"]
        
            # Add volume name and DeleteOn to snapshot for easier identification
            snapshot.create_tags(Tags=[{'Key': 'Name','Value': volumename},{'Key': 'DeleteOn','Value': delete_on}])
