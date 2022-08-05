from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.utils.encoding import filepath_to_uri

from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import setting


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

    def __init__(self, **settings):
        super().__init__(**settings)

    def get_default_settings(self):
        settings_dict = super().get_default_settings()
        settings_dict.update({
            "alternate_bucket_name": setting("AWS_STORAGE_ALTERNATE_BUCKET_NAME"),
            "alternate_custom_domain": setting("AWS_S3_ALTERNATE_CUSTOM_DOMAIN")
        })
        return settings_dict

    def url(self, name, parameters=None, expire=None, http_method=None):
        params = parameters.copy() if parameters else {}
        if self.exists(name):
            r = self._url(name, parameters=params, expire=expire, http_method=http_method)
        else:
            if self.alternate_bucket_name:
                params['Bucket'] = self.alternate_bucket_name
                r = self._url(name, parameters=params, expire=expire, http_method=http_method)
        return r

    def _url(self, name, parameters=None, expire=None, http_method=None):
        """
        Similar to super().url() except that it allows the caller to provide
        an alternate bucket name in parameters['Bucket']
        """
        # Preserve the trailing slash after normalizing the path.
        name = self._normalize_name(self._clean_name(name))
        params = parameters.copy() if parameters else {}
        if expire is None:
            expire = self.querystring_expire

        if self.custom_domain:
            bucket_name = params.pop('Bucket', None)
            if bucket_name is None or self.alternate_custom_domain is None:
                custom_domain = self.custom_domain
            else:
                custom_domain = self.alternate_custom_domain
            url = '{}//{}/{}{}'.format(
                self.url_protocol,
                custom_domain,
                filepath_to_uri(name),
                '?{}'.format(urlencode(params)) if params else '',
            )

            if self.querystring_auth and self.cloudfront_signer:
                expiration = datetime.utcnow() + timedelta(seconds=expire)
                return self.cloudfront_signer.generate_presigned_url(url, date_less_than=expiration)

            return url

        if params.get('Bucket') is None:
            params['Bucket'] = self.bucket.name
        params['Key'] = name
        url = self.bucket.meta.client.generate_presigned_url('get_object', Params=params,
                                                             ExpiresIn=expire, HttpMethod=http_method)
        if self.querystring_auth:
            return url
        return self._strip_signing_parameters(url)


class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    location = 'private'
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
