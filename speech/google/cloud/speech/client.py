# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Basic client for Google Cloud Speech API."""

import os

from google.cloud.client import Client as BaseClient
from google.cloud.environment_vars import DISABLE_GRPC

from google.cloud.speech._gax import GAPICSpeechAPI
from google.cloud.speech._http import HTTPSpeechAPI
from google.cloud.speech.sample import Sample


_USE_GAX = not os.getenv(DISABLE_GRPC, False)


class Client(BaseClient):
    """Client to bundle configuration needed for API requests.

    :type credentials: :class:`~google.auth.credentials.Credentials`
    :param credentials: (Optional) The OAuth2 Credentials to use for this
                        client. If not passed (and if no ``http`` object is
                        passed), falls back to the default inferred from the
                        environment.

    :type http: :class:`~httplib2.Http`
    :param http: (Optional) HTTP object to make requests. Can be any object
                 that defines ``request()`` with the same interface as
                 :meth:`~httplib2.Http.request`. If not passed, an
                 ``http`` object is created that is bound to the
                 ``credentials`` for the current object.

    :type use_gax: bool
    :param use_gax: (Optional) Explicitly specifies whether
                    to use the gRPC transport (via GAX) or HTTP. If unset,
                    falls back to the ``GOOGLE_CLOUD_DISABLE_GRPC`` environment
                    variable
    """

    SCOPE = ('https://www.googleapis.com/auth/cloud-platform',)
    """The scopes required for authenticating as an API consumer."""

    _speech_api = None

    def __init__(self, credentials=None, http=None, use_gax=None):
        super(Client, self).__init__(credentials=credentials, http=http)
        # Save on the actual client class whether we use GAX or not.
        if use_gax is None:
            self._use_gax = _USE_GAX
        else:
            self._use_gax = use_gax

    def sample(self, content=None, source_uri=None, stream=None, encoding=None,
               sample_rate=None):
        """Factory: construct Sample to use when making recognize requests.

        :type content: bytes
        :param content: (Optional) Bytes containing audio data.

        :type source_uri: str
        :param source_uri: (Optional) URI that points to a file that contains
                           audio data bytes as specified in RecognitionConfig.
                           Currently, only Google Cloud Storage URIs are
                           supported, which must be specified in the following
                           format: ``gs://bucket_name/object_name``.

        :type stream: file
        :param stream: (Optional) File like object to stream.

        :type encoding: str
        :param encoding: encoding of audio data sent in all RecognitionAudio
                         messages, can be one of: :attr:`~.Encoding.LINEAR16`,
                         :attr:`~.Encoding.FLAC`, :attr:`~.Encoding.MULAW`,
                         :attr:`~.Encoding.AMR`, :attr:`~.Encoding.AMR_WB`

        :type sample_rate: int
        :param sample_rate: Sample rate in Hertz of the audio data sent in all
                            requests. Valid values are: 8000-48000. For best
                            results, set the sampling rate of the audio source
                            to 16000 Hz. If that's not possible, use the
                            native sample rate of the audio source (instead of
                            re-sampling).

        :rtype: :class:`~google.cloud.speech.sample.Sample`
        :returns: Instance of ``Sample``.
        """
        return Sample(content=content, source_uri=source_uri, stream=stream,
                      encoding=encoding, sample_rate=sample_rate, client=self)

    @property
    def speech_api(self):
        """Helper for speech-related API calls."""
        if self._speech_api is None:
            if self._use_gax:
                self._speech_api = GAPICSpeechAPI(self)
            else:
                self._speech_api = HTTPSpeechAPI(self)
        return self._speech_api
