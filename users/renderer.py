from rest_framework import renderers

from utils.utils import convert_to_excel


class ExcelRenderer(renderers.BaseRenderer):
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        path = convert_to_excel(data)
        file = open(path, 'rb')
        return file.read()