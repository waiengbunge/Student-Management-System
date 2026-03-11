from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase
from apps.requests_app.services import RequestService


class RequestServiceTests(SimpleTestCase):
    @patch('apps.requests_app.services.Request')
    def test_create_request_returns_instance(self, mock_request):
        mock_request.objects.create.return_value = MagicMock(pk=1)
        r = RequestService.create_request(1, 2, 'Subj', 'Desc')
        self.assertIsNotNone(r)
        mock_request.objects.create.assert_called_once()

    @patch('apps.requests_app.services.RequestComment')
    def test_add_comment_creates(self, mock_comment):
        mock_comment.objects.create.return_value = MagicMock(pk=5)
        rc = RequestService.add_comment(1, 2, 'hello')
        mock_comment.objects.create.assert_called_once()
        self.assertIsNotNone(rc)

    @patch('apps.requests_app.services.RequestAttachment')
    def test_add_attachment_saves_file(self, mock_attachment):
        fa = MagicMock()
        mock_attachment.objects.create.return_value = fa
        # provide bytes-like file
        f = b'contents'
        res = RequestService.add_attachment(1, 2, f)
        mock_attachment.objects.create.assert_called_once()
        self.assertIsNotNone(res)

    @patch('apps.requests_app.services.Request')
    def test_close_request_sets_status(self, mock_request):
        inst = MagicMock()
        mock_request.objects.get.return_value = inst
        ok = RequestService.close_request(1)
        self.assertTrue(ok)
        self.assertEqual(inst.status, 'closed')
