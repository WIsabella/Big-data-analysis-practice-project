import json
from django.test import TestCase
from django.urls import reverse


class CreateOrderTest(TestCase):
    def test(self):
        url = reverse("create_order")
        bacterias = ['111', '222', '333', '444', '555', '666']

        # 直接传递字典，Django 会自动将其转换为 JSON
        response = self.client.post(
            url,
            data={'username': 'wqy', 'bacterias': bacterias},  # 不需要 json.dumps() 这里
            content_type='application/json'  # 设置请求类型为 JSON
        )

        # 断言状态码
        self.assertEqual(response.status_code, 201)
