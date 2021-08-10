from django.conf import settings
from zeep import Client
from django.utils.translation import ugettext_lazy as _

send_message = Client('http://smspro.nikita.kg/api/soap?wsdl').service.message

status_msg_map = {
    '0': _('We sent you confirmation SMS. Please check the message and enter the code'),
    '1': _('The service is temporarily unavailable. code: 1'),
    '2': _('The service is temporarily unavailable. code: 2'),
    '3': _('Phone number not found'),
    '4': _('The service is temporarily unavailable. code: 4'),
    '5': _('The service is temporarily unavailable. code: 5'),
    '6': _('The service is temporarily unavailable. code: 6'),
    '7': _('Invalid phone number format'),
    '8': _('The service is temporarily unavailable. code: 8'),
    '9': _('The service is temporarily unavailable. code: 9'),
    '10': _('The service is temporarily unavailable. code: 10'),
    '11': _('The service is temporarily unavailable. code: 11'),
}


def send_message_code(id, code, phone):
    sms_resp = send_message({
        'login': settings.NIKITA_LOGIN,
        'pwd': settings.NIKITA_PASSWORD,
        'sender': settings.NIKITA_SENDER,
        'id': id,
        'text': f'NZ.CLUB code: {code}',
        'phones': {
            'phone': phone,
        },
        'test': 2

    })
    return status_msg_map.get(sms_resp['status'])