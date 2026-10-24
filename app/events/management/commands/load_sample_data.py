from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from events.models import Event, Registration, Ticket


SAMPLE_EVENTS = [
    {
        'code': 'EVT001',
        'title': 'Tech Innovation Summit 2026',
        'description': (
            'Hội nghị công nghệ và đổi mới sáng tạo, nơi các chuyên gia chia sẻ xu hướng AI, '
            'điện toán đám mây và chuyển đổi số. Sự kiện tập trung vào trí tuệ nhân tạo, '
            'an toàn thông tin và các giải pháp chuyển đổi số trong doanh nghiệp.'
        ),
        'start': datetime(2026, 11, 15, 8, 0),
        'end': datetime(2026, 11, 15, 17, 0),
        'deadline': datetime(2026, 11, 13, 23, 59),
        'location': 'Trung tâm Hội nghị Quốc gia, Hà Nội',
        'category': 'Công nghệ',
        'capacity': 200,
        'attendees': 120,
        'featured_attendee': ('an.nguyen.eventhub.demo', 'Nguyễn Văn An'),
    },
    {
        'code': 'EVT002',
        'title': 'Ngày hội việc làm 2026',
        'description': (
            'Kết nối sinh viên, người tìm việc với doanh nghiệp; cung cấp cơ hội tuyển dụng, '
            'tư vấn nghề nghiệp và phỏng vấn trực tiếp.'
        ),
        'start': datetime(2026, 11, 20, 8, 30),
        'end': datetime(2026, 11, 20, 16, 30),
        'deadline': datetime(2026, 11, 18, 23, 59),
        'location': 'Đại học Thái Nguyên, Thái Nguyên',
        'category': 'Hướng nghiệp',
        'capacity': 150,
        'attendees': 86,
        'featured_attendee': ('binh.tran.eventhub.demo', 'Trần Thị Bình'),
    },
    {
        'code': 'EVT003',
        'title': 'Workshop Thiết kế sáng tạo',
        'description': (
            'Buổi thực hành về tư duy thiết kế, xây dựng giao diện và phát triển ý tưởng '
            'sản phẩm số dành cho người mới bắt đầu.'
        ),
        'start': datetime(2026, 11, 25, 14, 0),
        'end': datetime(2026, 11, 25, 17, 0),
        'deadline': datetime(2026, 11, 23, 23, 59),
        'location': 'Không gian sáng tạo, Hà Nội',
        'category': 'Workshop',
        'capacity': 60,
        'attendees': 35,
        'featured_attendee': ('duc.le.eventhub.demo', 'Lê Minh Đức'),
    },
    {
        'code': 'EVT004',
        'title': 'Hội thảo Khởi nghiệp trẻ',
        'description': (
            'Chia sẻ kinh nghiệm xây dựng mô hình kinh doanh, phát triển sản phẩm và gọi vốn '
            'dành cho các nhóm khởi nghiệp.'
        ),
        'start': datetime(2026, 12, 5, 9, 0),
        'end': datetime(2026, 12, 5, 12, 0),
        'deadline': datetime(2026, 12, 3, 23, 59),
        'location': 'Trung tâm hỗ trợ khởi nghiệp, Hà Nội',
        'category': 'Hội thảo',
        'capacity': 100,
        'attendees': 48,
        'featured_attendee': ('ha.pham.eventhub.demo', 'Phạm Thu Hà'),
    },
]


class Command(BaseCommand):
    help = 'Nạp dữ liệu sự kiện và lượt đăng ký minh họa, có thể chạy lặp an toàn.'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        created_events = 0
        created_registrations = 0
        created_tickets = 0
        next_ticket_number = len(SAMPLE_EVENTS) + 1

        for event_number, sample in enumerate(SAMPLE_EVENTS, start=1):
            event, was_created = Event.objects.get_or_create(
                event_code=sample['code'],
                defaults={
                    'title': sample['title'],
                    'description': sample['description'],
                    'event_date': timezone.make_aware(sample['start']),
                    'end_date': timezone.make_aware(sample['end']),
                    'registration_deadline': timezone.make_aware(sample['deadline']),
                    'location': sample['location'],
                    'category': sample['category'],
                    'capacity': sample['capacity'],
                },
            )
            created_events += int(was_created)

            for attendee_number in range(1, sample['attendees'] + 1):
                if attendee_number == 1:
                    username, attendee_name = sample['featured_attendee']
                    ticket_number = event_number
                else:
                    username = f'sample_{sample["code"].lower()}_{attendee_number:03d}'
                    attendee_name = f'Khách mời mẫu {attendee_number:03d}'
                    ticket_number = next_ticket_number
                    next_ticket_number += 1

                attendee, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@example.invalid',
                        'first_name': attendee_name,
                    },
                )
                if user_created:
                    attendee.set_unusable_password()
                    attendee.save(update_fields=['password'])

                registration, registration_created = Registration.objects.get_or_create(
                    user=attendee,
                    event=event,
                    defaults={
                        'attendee_name': attendee_name,
                        'status': Registration.STATUS_CONFIRMED,
                    },
                )
                created_registrations += int(registration_created)

                ticket_code = f'TKT-2026-{ticket_number:04d}'
                ticket, ticket_created = Ticket.objects.get_or_create(
                    registration=registration,
                    defaults={
                        'ticket_code': ticket_code,
                        'user': attendee,
                        'event': event,
                        'status': Ticket.STATUS_VALID,
                    },
                )
                if not ticket_created and ticket.ticket_code.startswith('TKT-2026-'):
                    ticket.ticket_code = ticket_code
                    ticket.save(update_fields=['ticket_code'])
                created_tickets += int(ticket_created)

        self.stdout.write(self.style.SUCCESS(
            'Hoàn tất dữ liệu minh họa: '
            f'{created_events} sự kiện mới, '
            f'{created_registrations} lượt đăng ký mới, '
            f'{created_tickets} vé mới. '
            f'Tổng sự kiện: {Event.objects.count()}. '
            'Tài khoản khách mẫu không có mật khẩu đăng nhập.'
        ))
