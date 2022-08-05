# Storing Django Static and Media Files on Amazon S3 with sharing of a production bucket with dev and staging environments 

Inspired by a [great tutorial on using S3 with Django](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/), this project shows how to
write a custom storage class that supports two S3 buckets.

# Use cases
This has been developed for a project in which we needed to allow sharing of a fairly large and stable production S3
bucket with temporary environments to speed up testing and avoid useless duplication of resources.  The temporary 
environment (testing, dev, staging) is configured to write and read from its own bucket.  However, when the temporary 
environment needs a resource that is not located in its own bucket, then it automatically tries to fetch it from the
production bucket.

The simple solution proposed could be used in any situation in which we want to allow a system to partially overwrite 
resources found in an original S3 repository without actually modifying the original resources.  Please note that the
custom storage class can be easily adapted for the other backends that are supported by [django-storages](https://github.com/jschneier/django-storages)

# Usage

Get the repository using
```
git clone https://github.com/sylvainletourneau/django-docker-s3-2buckets.git
```

Update the file ```aws-variables.env``` 
```
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
AWS_STORAGE_BUCKET_NAME=<THE_BUCKET_SPECIFIC_FOR_THIS_ENVIRONMENT>
AWS_STORAGE_ALTERNATE_BUCKET_NAME=<THE_PRODUCTION_OR_FALLBACK_BUCKET>
```

Then, please follow the original [tutorial](https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/) to
find out how to build and run.

# Main changes

This fork adds the following two variables in settings.py
```
AWS_STORAGE_ALTERNATE_BUCKET_NAME = os.getenv('AWS_STORAGE_ALTERNATE_BUCKET_NAME')
AWS_S3_ALTERNATE_CUSTOM_DOMAIN = f'{AWS_STORAGE_ALTERNATE_BUCKET_NAME}.s3.amazonaws.com'
```

The part that takes care of the fallback mechanism is located in `storage_backends.py` 
